# Setup Guide - Running the DAO Governance System

## Prerequisites Check

### 1. Python Environment ✓
You already have `.venv` set up. Dependencies are installed.

### 2. Ganache - Local Blockchain (REQUIRED)

You need Ganache running to test and deploy the smart contract. Choose ONE option:

#### **Option A: Ganache GUI (Recommended for beginners)**
1. Download from: https://trufflesuite.com/ganache/
2. Install and launch Ganache
3. Create a new workspace (Quickstart)
4. Ensure it's running on `HTTP://127.0.0.1:8545`

#### **Option B: Ganache CLI (Command line)**
1. Install Node.js first (if not installed): https://nodejs.org/
2. Install Ganache CLI:
   ```bash
   npm install -g ganache
   ```
3. Run Ganache:
   ```bash
   ganache --port 8545
   ```

## Verification Steps

### Step 1: Start Ganache
- **GUI**: Open Ganache application and start a workspace
- **CLI**: Run `ganache --port 8545` in a separate terminal

You should see accounts with ETH balances listed.

### Step 2: Activate Virtual Environment & Deploy
```bash
# Activate venv
.\.venv\Scripts\activate

# Deploy the contract
python scripts/deploy.py
```

Expected output:
```
Installing solc...
Compiling contract...
Deploying from account: 0x...
Contract deployed at: 0x...
Contract data saved to contract_data.json
```

### Step 3: Run Tests
```bash
python -m pytest -v
```

Expected output:
```
tests/test_contract.py::test_join_dao PASSED
tests/test_contract.py::test_submit_proposal PASSED
tests/test_contract.py::test_voting_and_processing PASSED
```

### Step 4: Run Interactive Demo
```bash
python scripts/interact.py
```

This will demonstrate the full workflow:
- Members joining
- Submitting a website
- Voting
- Processing the proposal
- Checking rewards

## Troubleshooting

### "Ganache not connected"
- Make sure Ganache is running on port 8545
- Check firewall settings
- Try restarting Ganache

### "Failed building wheel for cytoolz"
- Already handled - we're using `web3==7.14.0` with `toolz` instead

### Solc installation issues
- The script auto-installs solc 0.8.0
- If it fails, manually install: `python -m solcx.install v0.8.0`
