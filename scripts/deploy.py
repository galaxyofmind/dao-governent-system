import json
from web3 import Web3
from solcx import compile_standard, install_solc
import os

def deploy():
    # 1. Connect to Ganache
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    
    # Add middleware for Ganache compatibility
    from web3.middleware import ExtraDataToPOAMiddleware
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    
    try:
        # Test connection
        w3.eth.block_number
        print(f"Connected to Ganache. Block number: {w3.eth.block_number}")
    except Exception as e:
        print(f"Failed to connect to Ganache: {e}")
        print("Please ensure Ganache is running on port 8545.")
        return

    # 2. Install Solc
    print("Installing solc...")
    install_solc("0.8.0")

    # 3. Compile
    print("Compiling contract...")
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

    # 4. Deploy
    # Use the first account as deployer
    deployer_account = w3.eth.accounts[0]
    print(f"Deploying from account: {deployer_account}")

    ReputationDAO = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = ReputationDAO.constructor().transact({"from": deployer_account})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Contract deployed at: {tx_receipt.contractAddress}")

    # 5. Save data
    data = {
        "address": tx_receipt.contractAddress,
        "abi": abi
    }
    
    # Save to root directory
    with open("contract_data.json", "w") as f:
        json.dump(data, f, indent=4)
    print("Contract data saved to contract_data.json")
    
    # Save to frontend directory
    frontend_path = os.path.join("frontend", "contract_data.json")
    with open(frontend_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Contract data saved to {frontend_path}")

if __name__ == "__main__":
    deploy()
