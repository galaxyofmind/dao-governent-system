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
    """Test 1: Verify users can join DAO and receive initial tokens"""
    account = w3.eth.accounts[1]
    
    # Join
    contract.functions.joinDAO().transact({"from": account})
    
    # Check member
    member = contract.functions.members(account).call()
    assert member[0] == True # isMember
    assert member[1] == 100 # Initial tokens

def test_submit_proposal(w3, contract):
    """Test 2: Verify members can submit proposals"""
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

def test_voting_no_immediate_rewards(w3, contract):
    """Test 3: Verify voters don't receive immediate rewards when voting"""
    voters = w3.eth.accounts[2:5]
    for v in voters:
        if not contract.functions.members(v).call()[0]:
            contract.functions.joinDAO().transact({"from": v})

    proposer = w3.eth.accounts[1]
    if not contract.functions.members(proposer).call()[0]:
        contract.functions.joinDAO().transact({"from": proposer})
        
    tx = contract.functions.submitWebsite("http://no-reward-test.com").transact({"from": proposer})
    w3.eth.wait_for_transaction_receipt(tx)
    
    proposal_id = contract.functions.proposalCount().call() - 1
    
    # Check tokens before voting
    voter_before = contract.functions.members(voters[0]).call()
    tokens_before = voter_before[1]
    
    # Vote
    contract.functions.vote(proposal_id, 0).transact({"from": voters[0]})
    
    # Check tokens after voting - should be same (no immediate reward)
    voter_after = contract.functions.members(voters[0]).call()
    tokens_after = voter_after[1]
    
    assert tokens_after == tokens_before, "Voter should not receive immediate reward"

def test_majority_voters_get_rewards(w3, contract):
    """Test 4: Verify only majority voters receive rewards after finalization"""
    voters = w3.eth.accounts[5:8]
    for v in voters:
        if not contract.functions.members(v).call()[0]:
            contract.functions.joinDAO().transact({"from": v})

    proposer = w3.eth.accounts[1]
    
    tx = contract.functions.submitWebsite("http://majority-test.com").transact({"from": proposer})
    w3.eth.wait_for_transaction_receipt(tx)
    
    proposal_id = contract.functions.proposalCount().call() - 1
    
    # Vote: 2 for Scam, 1 for Safe
    contract.functions.vote(proposal_id, 0).transact({"from": voters[0]})  # Scam
    contract.functions.vote(proposal_id, 0).transact({"from": voters[1]})  # Scam
    contract.functions.vote(proposal_id, 3).transact({"from": voters[2]})  # Safe
    
    # Check tokens before finalization
    voter0_before = contract.functions.members(voters[0]).call()[1]
    voter1_before = contract.functions.members(voters[1]).call()[1]
    voter2_before = contract.functions.members(voters[2]).call()[1]
    
    # Process proposal
    contract.functions.processProposal(proposal_id).transact({"from": proposer})
    
    # Check tokens after finalization
    voter0_after = contract.functions.members(voters[0]).call()[1]
    voter1_after = contract.functions.members(voters[1]).call()[1]
    voter2_after = contract.functions.members(voters[2]).call()[1]
    
    # Majority voters (voted Scam) should get 10 tokens
    assert voter0_after == voter0_before + 10, "Majority voter 1 should receive 10 tokens"
    assert voter1_after == voter1_before + 10, "Majority voter 2 should receive 10 tokens"
    
    # Minority voter (voted Safe) should get 0 tokens
    assert voter2_after == voter2_before, "Minority voter should receive 0 tokens"

def test_proposer_receives_reward(w3, contract):
    """Test 5: Verify proposer receives 20 tokens when proposal is finalized"""
    proposer = w3.eth.accounts[1]
    voters = w3.eth.accounts[2:5]
    
    # Get proposer tokens before
    proposer_before = contract.functions.members(proposer).call()[1]
    
    tx = contract.functions.submitWebsite("http://proposer-reward-test.com").transact({"from": proposer})
    w3.eth.wait_for_transaction_receipt(tx)
    
    proposal_id = contract.functions.proposalCount().call() - 1
    
    # Vote to reach threshold
    for i, voter in enumerate(voters):
        contract.functions.vote(proposal_id, 0).transact({"from": voter})
    
    # Process proposal
    contract.functions.processProposal(proposal_id).transact({"from": proposer})
    
    # Check proposer tokens after
    proposer_after = contract.functions.members(proposer).call()[1]
    
    assert proposer_after == proposer_before + 20, "Proposer should receive 20 tokens"

def test_duplicate_vote_prevention(w3, contract):
    """Test 6: Verify members cannot vote twice on same proposal"""
    voter = w3.eth.accounts[2]
    proposer = w3.eth.accounts[1]
    
    tx = contract.functions.submitWebsite("http://duplicate-vote-test.com").transact({"from": proposer})
    w3.eth.wait_for_transaction_receipt(tx)
    
    proposal_id = contract.functions.proposalCount().call() - 1
    
    # First vote should succeed
    contract.functions.vote(proposal_id, 0).transact({"from": voter})
    
    # Second vote should fail
    with pytest.raises(Exception) as exc_info:
        contract.functions.vote(proposal_id, 1).transact({"from": voter})
    
    assert "Already voted" in str(exc_info.value)

def test_vote_threshold_enforcement(w3, contract):
    """Test 7: Verify proposal requires minimum 3 votes to finalize"""
    proposer = w3.eth.accounts[1]
    voter = w3.eth.accounts[2]
    
    tx = contract.functions.submitWebsite("http://threshold-test.com").transact({"from": proposer})
    w3.eth.wait_for_transaction_receipt(tx)
    
    proposal_id = contract.functions.proposalCount().call() - 1
    
    # Only 1 vote
    contract.functions.vote(proposal_id, 0).transact({"from": voter})
    
    # Try to process with insufficient votes
    with pytest.raises(Exception) as exc_info:
        contract.functions.processProposal(proposal_id).transact({"from": proposer})
    
    assert "Not enough votes" in str(exc_info.value)

def test_non_member_cannot_vote(w3, contract):
    """Test 8: Verify non-members cannot vote"""
    proposer = w3.eth.accounts[1]
    non_member = w3.eth.accounts[9]  # Account that hasn't joined
    
    tx = contract.functions.submitWebsite("http://non-member-test.com").transact({"from": proposer})
    w3.eth.wait_for_transaction_receipt(tx)
    
    proposal_id = contract.functions.proposalCount().call() - 1
    
    # Non-member tries to vote
    with pytest.raises(Exception) as exc_info:
        contract.functions.vote(proposal_id, 0).transact({"from": non_member})
    
    assert "Not a member" in str(exc_info.value)

def test_get_member_count(w3, contract):
    """Test 9: Verify member count is accurate"""
    initial_count = contract.functions.getMemberCount().call()
    
    new_member = w3.eth.accounts[8]
    if not contract.functions.members(new_member).call()[0]:
        contract.functions.joinDAO().transact({"from": new_member})
        
        new_count = contract.functions.getMemberCount().call()
        assert new_count == initial_count + 1, "Member count should increment"

def test_get_proposal_voters(w3, contract):
    """Test 10: Verify getProposalVoters returns correct voter list"""
    proposer = w3.eth.accounts[1]
    voters = w3.eth.accounts[2:5]
    
    tx = contract.functions.submitWebsite("http://voter-list-test.com").transact({"from": proposer})
    w3.eth.wait_for_transaction_receipt(tx)
    
    proposal_id = contract.functions.proposalCount().call() - 1
    
    # Cast votes
    for voter in voters:
        contract.functions.vote(proposal_id, 0).transact({"from": voter})
    
    # Get voter list
    voter_list = contract.functions.getProposalVoters(proposal_id).call()
    
    assert len(voter_list) == 3, "Should have 3 voters"
    for voter in voters:
        assert voter in voter_list, f"Voter {voter} should be in list"

def test_get_voter_choice(w3, contract):
    """Test 11: Verify getVoterChoice returns correct vote option"""
    proposer = w3.eth.accounts[1]
    voter = w3.eth.accounts[2]
    
    tx = contract.functions.submitWebsite("http://voter-choice-test.com").transact({"from": proposer})
    w3.eth.wait_for_transaction_receipt(tx)
    
    proposal_id = contract.functions.proposalCount().call() - 1
    
    # Vote for option 2 (Normal)
    contract.functions.vote(proposal_id, 2).transact({"from": voter})
    
    # Get voter choice
    choice = contract.functions.getVoterChoice(proposal_id, voter).call()
    
    assert choice == 2, "Voter choice should be option 2 (Normal)"
