#!/usr/bin/env python3
"""
Test script to verify joinDAO function with name parameter
"""
import json
from web3 import Web3

def test_join_dao():
    # Connect to Ganache
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    
    if not w3.is_connected():
        print("❌ Cannot connect to Ganache!")
        return
    
    print("✅ Connected to Ganache")
    
    # Load contract data
    with open('contract_data.json', 'r') as f:
        contract_data = json.load(f)
    
    contract = w3.eth.contract(
        address=contract_data['address'],
        abi=contract_data['abi']
    )
    
    print(f"✅ Contract loaded at: {contract_data['address']}")
    
    # Get accounts
    accounts = w3.eth.accounts
    print(f"\n📋 Available accounts: {len(accounts)}")
    
    # Test joining DAO with account 1 (account 0 is admin)
    test_account = accounts[1]
    test_name = "Alice"
    
    print(f"\n🧪 Testing joinDAO with:")
    print(f"   Account: {test_account}")
    print(f"   Name: {test_name}")
    
    try:
        # Check if already a member
        member_info = contract.functions.getMemberInfo(test_account).call()
        if member_info[0]:  # isMember
            print(f"\n⚠️  Account is already a member!")
            print(f"   Name: {member_info[6]}")
            print(f"   Tokens: {member_info[1]}")
            return
        
        # Join DAO
        tx_hash = contract.functions.joinDAO(test_name).transact({
            'from': test_account
        })
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt['status'] == 1:
            print(f"\n✅ Successfully joined DAO!")
            print(f"   Transaction hash: {tx_hash.hex()}")
            
            # Verify member info
            member_info = contract.functions.getMemberInfo(test_account).call()
            print(f"\n📊 Member Info:")
            print(f"   Is Member: {member_info[0]}")
            print(f"   Tokens: {member_info[1]}")
            print(f"   Role: {member_info[2]} (0=Member, 1=Moderator, 2=Admin)")
            print(f"   Name: {member_info[6]}")
            print(f"   Proposals Submitted: {member_info[4]}")
            print(f"   Votes Count: {member_info[5]}")
            
            # Check total members
            total_members = contract.functions.getMemberCount().call()
            print(f"\n👥 Total DAO Members: {total_members}")
            
        else:
            print(f"\n❌ Transaction failed!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_join_dao()
