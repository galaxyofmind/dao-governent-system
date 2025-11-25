# DAO Governance System for Website Reputation

A simple DAO (Decentralized Autonomous Organization) system where members can submit websites suspected of fraud, vote on their reputation, and earn rewards.

## Project Structure
- `contracts/`: Solidity smart contracts (`ReputationDAO.sol`).
- `scripts/`: Python scripts for deployment (`deploy.py`) and interaction (`interact.py`).
- `tests/`: Unit tests (`test_contract.py`).

## Prerequisites
- Python 3.x
- Ganache (running on `http://127.0.0.1:8545`)

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Ganache**:
   Open Ganache and ensure it's running on port 8545.

## Usage

### 1. Deploy the Contract
```bash
python scripts/deploy.py
```
This will compile the contract and deploy it to your local Ganache blockchain. It saves the contract address and ABI to `contract_data.json`.

### 2. Interact with the DAO
Run the interaction script to see a demo flow (Joining, Submitting, Voting, Finalizing):
```bash
python scripts/interact.py
```

### 3. Run Tests
```bash
pytest
```

## Features
- **Membership**: Users join to become members and receive initial tokens.
- **Proposals**: Members submit URLs for evaluation.
- **Voting**: Members vote (Scam, High Risk, Normal, Safe).
- **Rewards**: Members earn tokens for voting and for successful proposals.
- **Reputation**: Websites are classified based on the majority vote.
- **Web Frontend**: Modern web interface with MetaMask integration.

## Usage

### Backend (Python Scripts)

#### 1. Deploy the Contract
```bash
python scripts/deploy.py
```
This will compile the contract and deploy it to your local Ganache blockchain. It saves the contract address and ABI to `contract_data.json`.

#### 2. Interact with the DAO
Run the interaction script to see a demo flow (Joining, Submitting, Voting, Finalizing):
```bash
python scripts/interact.py
```

#### 3. Run Tests
```bash
pytest
```

### Frontend (Web Interface)

#### 1. Start the Frontend Server
```bash
python serve_frontend.py
```

#### 2. Open in Browser
Navigate to: `http://localhost:8000`

#### 3. Connect MetaMask
- Install MetaMask browser extension
- Add Ganache network (RPC: http://127.0.0.1:8545, Chain ID: 1337)
- Import a Ganache account using its private key
- Click "Connect Wallet" in the web interface

#### 4. Use the DApp
- **Join DAO**: Become a member and receive 100 tokens
- **Submit Website**: Propose a website for evaluation
- **Vote**: Cast your vote on proposals
- **Finalize**: Process proposals when they reach 3+ votes

See `frontend/README.md` for detailed frontend documentation.
