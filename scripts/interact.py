import json
from web3 import Web3
import os

class DAOClient:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        
        # Add middleware for Ganache compatibility
        from web3.middleware import ExtraDataToPOAMiddleware
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        
        try:
            # Test connection
            self.w3.eth.block_number
        except Exception as e:
            raise Exception(f"Failed to connect to Ganache: {e}")
        
        # Load contract data
        if not os.path.exists("contract_data.json"):
            raise Exception("contract_data.json not found. Please run deploy.py first.")
            
        with open("contract_data.json", "r") as f:
            data = json.load(f)
            self.contract_address = data["address"]
            self.abi = data["abi"]
        
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
        self.accounts = self.w3.eth.accounts

    def join_dao(self, account_index):
        account = self.accounts[account_index]
        try:
            tx_hash = self.contract.functions.joinDAO().transact({"from": account})
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Account {account} joined DAO")
        except Exception as e:
            print(f"Error joining DAO: {e}")

    def submit_website(self, account_index, url):
        account = self.accounts[account_index]
        try:
            tx_hash = self.contract.functions.submitWebsite(url).transact({"from": account})
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Account {account} submitted website: {url}")
        except Exception as e:
            print(f"Error submitting website: {e}")

    def vote(self, account_index, proposal_id, option):
        # 0: Scam, 1: HighRisk, 2: Normal, 3: Safe
        account = self.accounts[account_index]
        options = ["Scam", "HighRisk", "Normal", "Safe"]
        try:
            tx_hash = self.contract.functions.vote(proposal_id, option).transact({"from": account})
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Account {account} voted {options[option]} on proposal {proposal_id}")
        except Exception as e:
            print(f"Error voting: {e}")

    def process_proposal(self, account_index, proposal_id):
        account = self.accounts[account_index]
        try:
            tx_hash = self.contract.functions.processProposal(proposal_id).transact({"from": account})
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Proposal {proposal_id} processed")
        except Exception as e:
            print(f"Error processing proposal: {e}")

    def get_proposal_status(self, proposal_id):
        try:
            p = self.contract.functions.proposals(proposal_id).call()
            # p: (id, url, proposer, startTime, processed, finalStatus)
            status_enum = ["Scam", "HighRisk", "Normal", "Safe"]
            status = status_enum[p[5]] if p[4] else "Pending"
            print(f"Proposal {proposal_id} ({p[1]}): Status = {status}, Processed = {p[4]}")
            
            # Get votes
            votes = self.contract.functions.getProposalVotes(proposal_id).call()
            print(f"  Votes: Scam={votes[0]}, HighRisk={votes[1]}, Normal={votes[2]}, Safe={votes[3]}")
        except Exception as e:
            print(f"Error getting status: {e}")

    def get_member_info(self, account_index):
        account = self.accounts[account_index]
        member = self.contract.functions.members(account).call()
        # member: (isMember, tokens)
        print(f"Member {account}: Joined={member[0]}, Tokens={member[1]}")

if __name__ == "__main__":
    client = DAOClient()
    
    print("\n--- 1. Members Joining ---")
    client.join_dao(0)
    client.join_dao(1)
    client.join_dao(2)
    client.join_dao(3)
    
    print("\n--- 2. Submit Proposal ---")
    client.submit_website(0, "http://suspicious-site.com")
    
    print("\n--- 3. Voting ---")
    # Proposal 0
    client.vote(1, 0, 0) # Vote Scam
    client.vote(2, 0, 0) # Vote Scam
    client.vote(3, 0, 1) # Vote HighRisk
    
    print("\n--- 4. Check Status Before Finalization ---")
    client.get_proposal_status(0)
    
    print("\n--- 5. Process Proposal ---")
    client.process_proposal(0, 0)
    
    print("\n--- 6. Final Status & Rewards ---")
    client.get_proposal_status(0)
    client.get_member_info(0) # Proposer should have rewards
    client.get_member_info(1) # Voter should have rewards
