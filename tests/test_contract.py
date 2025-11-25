import pytest
from web3 import Web3
from solcx import compile_standard, install_solc
import os

# Connect to Ganache
@pytest.fixture(scope="module")
def w3():
    w3_instance = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    
    # Add middleware for Ganache compatibility
    from web3.middleware import ExtraDataToPOAMiddleware
    w3_instance.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    
    try:
        # Test connection
        w3_instance.eth.block_number
    except Exception as e:
        raise AssertionError(f"Ganache not connected: {e}")
    
    return w3_instance

# Deploy contract once for all tests
@pytest.fixture(scope="module")
def contract(w3):
    install_solc("0.8.0")
    
    contract_path = os.path.join("contracts", "ReputationDAO.sol")
    with open(contract_path, "r") as f:
        contract_source = f.read()

    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"ReputationDAO.sol": {"content": contract_source}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                    }
                }
            },
        },
        solc_version="0.8.0",
    )

    bytecode = compiled_sol["contracts"]["ReputationDAO.sol"]["ReputationDAO"]["evm"]["bytecode"]["object"]
    abi = compiled_sol["contracts"]["ReputationDAO.sol"]["ReputationDAO"]["abi"]

    ReputationDAO = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = ReputationDAO.constructor().transact({"from": w3.eth.accounts[0]})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

def test_join_dao(w3, contract):
    account = w3.eth.accounts[1]
    # Check not member initially (if fresh)
    # Since scope is module, we assume fresh deployment
    
    # Join
    contract.functions.joinDAO().transact({"from": account})
    
    # Check member
    member = contract.functions.members(account).call()
    assert member[0] == True # isMember
    assert member[1] == 100 # Initial tokens

def test_submit_proposal(w3, contract):
    account = w3.eth.accounts[1]
    # Ensure member
    if not contract.functions.members(account).call()[0]:
        contract.functions.joinDAO().transact({"from": account})

    initial_count = contract.functions.proposalCount().call()
    
    contract.functions.submitWebsite("http://test.com").transact({"from": account})
    
    new_count = contract.functions.proposalCount().call()
    assert new_count == initial_count + 1
    
    p = contract.functions.proposals(initial_count).call()
    assert p[1] == "http://test.com"
    assert p[2] == account

def test_voting_and_processing(w3, contract):
    # Setup accounts
    voters = w3.eth.accounts[2:5]
    for v in voters:
        if not contract.functions.members(v).call()[0]:
            contract.functions.joinDAO().transact({"from": v})

    # Create proposal
    proposer = w3.eth.accounts[1]
    # Ensure proposer is member
    if not contract.functions.members(proposer).call()[0]:
        contract.functions.joinDAO().transact({"from": proposer})
        
    tx = contract.functions.submitWebsite("http://vote-test.com").transact({"from": proposer})
    w3.eth.wait_for_transaction_receipt(tx)
    
    # Get proposal ID (it's the last one)
    proposal_id = contract.functions.proposalCount().call() - 1
    
    # Vote
    # 0: Scam
    contract.functions.vote(proposal_id, 0).transact({"from": voters[0]})
    contract.functions.vote(proposal_id, 0).transact({"from": voters[1]})
    contract.functions.vote(proposal_id, 3).transact({"from": voters[2]}) # Safe
    
    # Check votes
    votes = contract.functions.getProposalVotes(proposal_id).call()
    assert votes[0] == 2
    assert votes[3] == 1
    
    # Process
    contract.functions.processProposal(proposal_id).transact({"from": proposer})
    
    p = contract.functions.proposals(proposal_id).call()
    assert p[4] == True # Processed
    assert p[5] == 0 # Scam wins
    
    # Check rewards
    # Voter gets 10
    voter_info = contract.functions.members(voters[0]).call()
    assert voter_info[1] == 110 # 100 + 10
