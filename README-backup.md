# DAO Governance System for Website Reputation Evaluation

## 1. Project Title and Group Members

### Project Name
**DAO Governance System for Website Reputation and Fraud Prevention**

### Group Members
<!-- TODO: Fill in your group member information -->
| Name | Student ID | Role |
|------|------------|------|
| Đoàn Việt Hoàng | 29219149787 | Lead |
| Nguyễn Ngọc Ấn |  |  |
| Ngô Nhật Quang |  |  |


---

## 2. Project Description

### What the Project Does

This project implements a **Decentralized Autonomous Organization (DAO)** that enables community-driven evaluation of website reputation to prevent fraud and identify security risks. The system allows:

- **Democratic Governance**: Members vote collectively on website reputation
- **Transparent Decision-Making**: All votes recorded on blockchain
- **Incentive Mechanism**: Token rewards for participation
- **Fraud Prevention**: Community-based website classification
- **Role-Based Access**: Admin, Moderator, and Member roles (not implemented yet :>)

### Problem It Solves

**Problem**: Traditional website reputation systems are centralized and vulnerable to:
- Too many platforms operate individually
- Manipulation by authorities
- Lack of transparency
- No user incentives for participation

**Our Solution**: A decentralized system where:
- ✅ No Central Authority: Community-driven decisions
- ✅ Transparent: All votes visible on blockchain
- ✅ Incentivized: Users earn tokens for participation
- ✅ Democratic: Majority vote determines outcome
- ✅ Fast: Quick community response to threats
- ✅ Immutable: Cannot be altered or censored

### Key Features

1. **Member Management**
   - Join DAO and receive 100 initial tokens
   - Track member statistics (proposals, votes, tokens)
   - [ ] Role-based permissions (Member, Moderator, Admin) - not implemented yet 

2. **Proposal System**
   - Submit suspicious websites for evaluation
   - Track proposal status (Pending/Scam/HighRisk/Normal/Safe)
   - View vote distribution in real-time

3. **Voting Mechanism**
   - Four reputation levels: Scam, High Risk, Normal, Safe
   - One vote per member per proposal
   - Earn 10 tokens per vote

4. **Finalization**
   - Requires minimum 3 votes
   - Majority vote determines final status
   - Proposer earns 20 tokens when finalized

5. **Web Interface**
   - Modern, responsive UI
   - MetaMask integration
   - Real-time blockchain updates
   - Search and filter functionality

---

## 3. Setup Instructions

### Prerequisites

Before starting, ensure you have:
- **Python 3.13+** installed
- **Ganache** (local blockchain)
- **MetaMask** browser extension
- **Git** (optional, for cloning)

### Step 1: Install Dependencies

#### Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.\.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

#### Install Python Packages
```bash
pip install -r requirements.txt
```

**Dependencies installed**:
- `web3` - Ethereum blockchain interaction
- `py-solc-x` - Solidity compiler
- `pytest` - Testing framework

### Step 2: Run Ganache

#### Option A: Ganache GUI (Recommended)
1. Download from: https://trufflesuite.com/ganache/
2. Install and launch Ganache
3. Click "Quickstart" to create a workspace
4. Verify it's running on `http://127.0.0.1:8545`

#### Option B: Ganache CLI
```bash
npm install -g ganache-cli
ganache-cli
```

**Important**: Keep Ganache running throughout development!

### Step 3: Deploy the Contract

```bash
# Ensure virtual environment is activated
.\.venv\Scripts\activate

# Run deployment script
python scripts/deploy.py
```

**Expected Output**:
```
Connected to Ganache. Block number: 0
Installing solc...
Compiling contract...
Deploying from account: 0x5EF08b21aF79953d9CAb48857a1Ae88bA68E5110
Contract deployed at: 0x216d21d1Efe6AB85873681eae9eBc22E97403860
Contract data saved to contract_data.json
```

**What Happens**:
- Connects to Ganache
- Compiles `ReputationDAO.sol`
- Deploys contract to blockchain
- Saves address and ABI to `contract_data.json`

---

## 4. Usage Instructions

### Backend Usage (Python Scripts)

#### Step 1: Deploy Contract (if not already done)
```bash
python scripts/deploy.py
```

#### Step 2: Run Interactive Demo
```bash
python scripts/interact.py
```

**Demo Flow**:
1. Four accounts join the DAO
2. First account submits a website
3. Three accounts vote on the proposal
4. Proposal is finalized based on majority vote
5. Tokens are distributed to participants

### Frontend Usage (Web Interface)

#### Step 1: Start Frontend Server
```bash
python serve_frontend.py
```

**Server will start at**: `http://localhost:8000`

#### Step 2: Configure MetaMask

1. **Add Ganache Network**:
   - Network Name: `Ganache Local`
   - RPC URL: `http://127.0.0.1:8545`
   - Chain ID: `1337`
   - Currency Symbol: `ETH`

2. **Import Ganache Account**:
   - Open Ganache → Copy a private key
   - MetaMask → Import Account → Paste key

#### Step 3: Use the DApp

**Connect Wallet**:
1. Open `http://localhost:8000`
2. Click "Connect Wallet"
3. Approve MetaMask connection
4. Network auto-switches to Ganache

**Join DAO**:
1. Go to "Join DAO" tab
2. Click "Join DAO Now"
3. Confirm transaction in MetaMask
4. Receive 100 initial tokens

**Submit Website**:
1. Go to "Submit Website" tab
2. Enter website URL (e.g., `https://example.com`)
3. Click "Submit Proposal"
4. Confirm transaction

**Vote on Proposal**:
1. Go to "All Proposals" tab
2. Find a proposal
3. Click one of the vote buttons:
   - Vote Scam
   - Vote High Risk
   - Vote Normal
   - Vote Safe
4. Earn 10 tokens

**Finalize Proposal**:
1. When proposal has 3+ votes
2. Click "Finalize Proposal" button
3. Proposer earns 20 tokens
4. Final status is determined

**Search Proposals**:
1. Go to "All Proposals" tab
2. Use search box at top right
3. Type URL or proposal ID
4. Results filter in real-time

---

## 5. Smart Contract Functions

### Public Functions (Anyone Can Call)

#### `joinDAO()`
**Description**: Allows a user to become a DAO member  
**Requirements**: User must not already be a member  
**Effects**:
- Sets `isMember` to true
- Grants 100 initial tokens
- Records join timestamp
- Increments total member count

**Example**:
```javascript
await contract.methods.joinDAO().send({ from: account });
```

---

#### `submitWebsite(string _url)`
**Description**: Submit a website URL for reputation evaluation  
**Parameters**:
- `_url`: Website URL to evaluate

**Requirements**: Caller must be a DAO member  
**Effects**:
- Creates new proposal
- Sets proposer address
- Initializes vote counts to zero
- Increments proposal count

**Example**:
```javascript
await contract.methods.submitWebsite("https://example.com").send({ from: account });
```

---

#### `vote(uint _proposalId, uint8 _option)`
**Description**: Cast a vote on a proposal  
**Parameters**:
- `_proposalId`: ID of the proposal to vote on
- `_option`: Vote choice (0=Scam, 1=HighRisk, 2=Normal, 3=Safe)

**Requirements**:
- Caller must be a member
- Proposal must exist and be active
- Caller must not have already voted
- Proposal must not be processed

**Effects**:
- Increments vote count for chosen option
- Marks member as having voted
- Awards 10 tokens to voter
- Increments member's vote count

**Example**:
```javascript
await contract.methods.vote(0, 0).send({ from: account }); // Vote "Scam" on proposal 0
```

---

#### `processProposal(uint _proposalId)`
**Description**: Finalize a proposal and determine final status  
**Parameters**:
- `_proposalId`: ID of the proposal to process

**Requirements**:
- Proposal must exist
- Proposal must not already be processed
- Proposal must be active
- Must have at least 3 votes (VOTE_THRESHOLD)

**Effects**:
- Calculates majority vote
- Sets final reputation status
- Marks proposal as processed
- Awards 20 tokens to proposer

**Example**:
```javascript
await contract.methods.processProposal(0).send({ from: account });
```

---

### View Functions (Read-Only)

#### `proposalCount()`
**Returns**: Total number of proposals submitted  
**Example**:
```javascript
const count = await contract.methods.proposalCount().call();
```

---

#### `totalMembers()`
**Returns**: Total number of DAO members  
**Example**:
```javascript
const members = await contract.methods.totalMembers().call();
```

---

#### `getMemberCount()`
**Returns**: Current count of active members  
**Example**:
```javascript
const count = await contract.methods.getMemberCount().call();
```

---

#### `getProposalVotes(uint _proposalId)`
**Description**: Get vote distribution for a proposal  
**Parameters**:
- `_proposalId`: Proposal ID to query

**Returns**: Tuple of (scamVotes, highRiskVotes, normalVotes, safeVotes)  
**Example**:
```javascript
const votes = await contract.methods.getProposalVotes(0).call();
// votes = [2, 1, 0, 1] // 2 Scam, 1 HighRisk, 0 Normal, 1 Safe
```

---

#### `getMemberInfo(address _member)`
**Description**: Get detailed information about a member  
**Parameters**:
- `_member`: Member address to query

**Returns**: Tuple of (isMember, tokens, role, joinedAt, proposalsSubmitted, votesCount)  
**Example**:
```javascript
const info = await contract.methods.getMemberInfo(account).call();
// info = [true, 120, 0, 1732567890, 1, 2]
```

---

#### `getAllMembers()`
**Returns**: Array of all member addresses  
**Example**:
```javascript
const members = await contract.methods.getAllMembers().call();
// members = ["0x5EF...", "0x7AB...", ...]
```

---

#### `isProposalActive(uint _proposalId)`
**Description**: Check if a proposal is active  
**Parameters**:
- `_proposalId`: Proposal ID to check

**Returns**: Boolean (true if active, false if deactivated)  
**Example**:
```javascript
const active = await contract.methods.isProposalActive(0).call();
```

---

### Admin Functions (Admin Only)

#### `setMemberRole(address _member, Role _role)`
**Description**: Assign a role to a member  
**Parameters**:
- `_member`: Member address
- `_role`: Role to assign (0=Member, 1=Moderator, 2=Admin)

**Requirements**: Caller must be admin  
**Example**:
```javascript
await contract.methods.setMemberRole(memberAddress, 1).send({ from: adminAccount });
```

---

#### `removeMember(address _member)`
**Description**: Remove a member from the DAO  
**Parameters**:
- `_member`: Member address to remove

**Requirements**:
- Caller must be admin
- Cannot remove admin

**Example**:
```javascript
await contract.methods.removeMember(memberAddress).send({ from: adminAccount });
```

---

#### `grantTokens(address _member, uint _amount)`
**Description**: Grant tokens to a member  
**Parameters**:
- `_member`: Member address
- `_amount`: Number of tokens to grant

**Requirements**: Caller must be admin  
**Example**:
```javascript
await contract.methods.grantTokens(memberAddress, 50).send({ from: adminAccount });
```

---

### Moderator Functions (Moderator/Admin Only)

#### `deactivateProposal(uint _proposalId)`
**Description**: Deactivate a spam or invalid proposal  
**Parameters**:
- `_proposalId`: Proposal ID to deactivate

**Requirements**:
- Caller must be moderator or admin
- Proposal must not be processed

**Example**:
```javascript
await contract.methods.deactivateProposal(0).send({ from: moderatorAccount });
```

---

### Constants

- `REWARD_AMOUNT`: 10 tokens (reward per vote)
- `VOTE_THRESHOLD`: 3 votes (minimum to finalize)

---

## 6. Testing Instructions

### Run All Tests

```bash
# Ensure virtual environment is activated
.\.venv\Scripts\activate

# Run pytest
python -m pytest -v
```

**Expected Output**:
```
tests/test_contract.py::test_join_dao PASSED                    [ 33%]
tests/test_contract.py::test_submit_proposal PASSED             [ 66%]
tests/test_contract.py::test_voting_and_processing PASSED       [100%]

===================== 3 passed in 2.49s =====================
```

### Test Descriptions

#### Test 1: `test_join_dao`
**What It Tests**:
- User can join the DAO
- Initial token balance is 100
- Member status is set correctly

**Validation**:
```python
assert member.isMember == True
assert member.tokens == 100
```

**What It Validates**:
- ✅ Membership registration works
- ✅ Initial tokens are granted
- ✅ Member data is stored correctly

---

#### Test 2: `test_submit_proposal`
**What It Tests**:
- Member can submit a website proposal
- Proposal is created with correct data
- Proposal count increments

**Validation**:
```python
assert proposal_count == 1
assert proposal.websiteUrl == test_url
assert proposal.proposer == accounts[0]
assert proposal.processed == False
```

**What It Validates**:
- ✅ Proposal creation works
- ✅ URL is stored correctly
- ✅ Proposer is recorded
- ✅ Initial state is correct

---

#### Test 3: `test_voting_and_processing`
**What It Tests**:
- Multiple members can vote
- Votes are counted correctly
- Tokens are awarded for voting
- Proposal can be finalized
- Final status is determined by majority
- Proposer receives reward

**Validation**:
```python
# Vote counting
assert votes[0] == 2  # 2 Scam votes
assert votes[3] == 1  # 1 Safe vote

# Token rewards
assert member1_after.tokens == 110  # 100 + 10 for voting
assert member2_after.tokens == 110

# Finalization
assert proposal_after.processed == True
assert proposal_after.finalStatus == 0  # Scam (majority)

# Proposer reward
assert proposer_after.tokens == 120  # 100 + 20 for proposal
```

**What It Validates**:
- ✅ Voting mechanism works
- ✅ Vote counts are accurate
- ✅ Duplicate voting is prevented
- ✅ Token rewards are distributed
- ✅ Majority vote determines outcome
- ✅ Proposer receives bonus reward
- ✅ Proposal status updates correctly

---

### Run Specific Test

```bash
# Run only join DAO test
pytest tests/test_contract.py::test_join_dao -v

# Run only voting test
pytest tests/test_contract.py::test_voting_and_processing -v
```

### Test Coverage

Our tests cover:
- ✅ **Member Management**: Join DAO, token allocation
- ✅ **Proposal System**: Submit, track, finalize
- ✅ **Voting Mechanism**: Cast votes, count votes, prevent duplicates
- ✅ **Token Economics**: Rewards for voting and proposing
- ✅ **Consensus**: Majority vote calculation
- ✅ **State Management**: Proposal status updates

---

## Additional Information

### Technology Stack

- **Blockchain**: Ethereum (Ganache local)
- **Smart Contract**: Solidity 0.8.0
- **Backend**: Python 3.13.9
- **Web3 Library**: Web3.py 7.14.0
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Testing**: pytest 9.0.1

### Project Structure

```
dao-governance/
├── contracts/          # Solidity smart contracts
├── scripts/            # Python deployment & interaction
├── tests/              # Unit tests
├── frontend/           # Web interface
├── .venv/              # Virtual environment (not in Git)
└── docs/               # Documentation
```

### Security Considerations

- ✅ Member-only actions enforced
- ✅ Duplicate vote prevention
- ✅ Vote threshold validation
- ✅ Role-based access control
- ✅ Input validation

### Future Enhancements

- Time-based voting periods
- Weighted voting by token holdings
- Proposal categories
- Member reputation scores
- Analytics dashboard
- IPFS integration for evidence
- Multi-chain deployment

---

## Contact Information

**Course**: DS441 - Blockchain Technology  
**Institution**: [Your University]  
**Instructor**: [Instructor Name]  

For questions or issues, please contact:
- [Your Email]
- [Group Leader Email]

---

## License

This project is created for educational purposes as part of DS441 coursework.

---

**Last Updated**: November 26, 2025  
**Version**: 1.0.0  
**Status**: Complete and Verified ✅
