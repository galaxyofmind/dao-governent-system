#!/usr/bin/env python3
"""
Reset/Clear DAO Data Script
This script redeploys the smart contract to clear all data and reset the system.
"""
import json
import os
from web3 import Web3
from solcx import compile_standard, install_solc
import sys

def main():
    print("=" * 60)
    print("🔄 DAO Data Reset Script")
    print("=" * 60)
    print()
    
    # Connect to Ganache
    print("📡 Connecting to Ganache...")
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    
    if not w3.is_connected():
        print("❌ Error: Cannot connect to Ganache!")
        print("   Please make sure Ganache is running on http://127.0.0.1:8545")
        sys.exit(1)
    
    print("✅ Connected to Ganache")
    print(f"   Chain ID: {w3.eth.chain_id}")
    print()
    
    # Get accounts
    accounts = w3.eth.accounts
    if not accounts:
        print("❌ Error: No accounts found in Ganache!")
        sys.exit(1)
    
    deployer = accounts[0]
    print(f"👤 Deployer account: {deployer}")
    print(f"   Balance: {w3.from_wei(w3.eth.get_balance(deployer), 'ether')} ETH")
    print()
    
    # Confirm reset
    print("⚠️  WARNING: This will reset ALL data!")
    print("   - All proposals will be deleted")
    print("   - All member data will be cleared")
    print("   - A new contract will be deployed")
    print()
    
    confirm = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Reset cancelled.")
        sys.exit(0)
    
    print()
    print("🔨 Compiling contract...")
    
    # Read contract source
    contract_path = os.path.join(os.path.dirname(__file__), '..', 'contracts', 'ReputationDAO.sol')
    with open(contract_path, 'r') as f:
        contract_source = f.read()
    
    # Install solc if needed
    try:
        install_solc('0.8.0')
    except:
        pass
    
    # Compile contract
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
    
    # Get bytecode and ABI
    contract_interface = compiled_sol['contracts']['ReputationDAO.sol']['ReputationDAO']
    bytecode = contract_interface['evm']['bytecode']['object']
    abi = contract_interface['abi']
    
    print("✅ Contract compiled successfully")
    print()
    
    # Deploy new contract
    print("🚀 Deploying new contract...")
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Build transaction
    tx_hash = Contract.constructor().transact({'from': deployer})
    
    # Wait for transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress
    
    print("✅ Contract deployed successfully!")
    print(f"   Contract address: {contract_address}")
    print(f"   Transaction hash: {tx_hash.hex()}")
    print(f"   Gas used: {tx_receipt.gasUsed}")
    print()
    
    # Save contract data
    contract_data = {
        "address": contract_address,
        "abi": abi
    }
    
    # Save to both root and frontend directories
    root_path = os.path.join(os.path.dirname(__file__), '..', 'contract_data.json')
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'contract_data.json')
    
    for path in [root_path, frontend_path]:
        with open(path, 'w') as f:
            json.dump(contract_data, f, indent=4)
        print(f"💾 Contract data saved to: {path}")
    
    print()
    print("=" * 60)
    print("✅ Data reset completed successfully!")
    print("=" * 60)
    print()
    print("📝 Next steps:")
    print("   1. Refresh your browser")
    print("   2. Reconnect your MetaMask wallet")
    print("   3. Start fresh with a clean DAO!")
    print()

if __name__ == "__main__":
    main()
