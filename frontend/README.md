# DAO Governance - Web Frontend

A modern, responsive web interface for the DAO Governance system built with vanilla HTML, CSS, and JavaScript with Web3.js integration.

## Features

### 🎨 Modern UI/UX
- **Dark Theme**: Beautiful dark mode design with gradient accents
- **Responsive**: Works perfectly on desktop, tablet, and mobile
- **Smooth Animations**: Micro-interactions and transitions
- **Real-time Updates**: Live blockchain data

### 🔗 Web3 Integration
- **MetaMask Connection**: Seamless wallet integration
- **Smart Contract Interaction**: Full CRUD operations
- **Transaction Handling**: User-friendly transaction flow
- **Error Handling**: Comprehensive error messages

### ⚡ Core Functionality
1. **Connect Wallet**: Connect MetaMask to interact with the DAO
2. **Join DAO**: Become a member and receive 100 initial tokens
3. **Submit Websites**: Propose websites for reputation evaluation
4. **Vote**: Cast votes on proposals (Scam, High Risk, Normal, Safe)
5. **Finalize**: Process proposals when vote threshold is met
6. **View Stats**: Real-time dashboard with proposals and token balance

## Prerequisites

- **MetaMask**: Browser extension installed
- **Ganache**: Local blockchain running on `http://127.0.0.1:8545`
- **Contract Deployed**: Smart contract must be deployed (see main README)

## Setup

### 1. Ensure Contract is Deployed
```bash
# From project root
.\.venv\Scripts\activate
python scripts/deploy.py
```

This creates `contract_data.json` which is automatically copied to the frontend folder.

### 2. Start Local Server

**Option A: Python HTTP Server (Recommended)**
```bash
# From the frontend directory
python -m http.server 8000
```

**Option B: Node.js HTTP Server**
```bash
npx http-server -p 8000
```

**Option C: VS Code Live Server**
- Install "Live Server" extension
- Right-click `index.html` → "Open with Live Server"

### 3. Open in Browser
Navigate to: `http://localhost:8000`

## Usage Guide

### Step 1: Connect MetaMask
1. Click "Connect Wallet" button
2. Approve MetaMask connection
3. Select your Ganache account

### Step 2: Join the DAO
1. Go to "Join DAO" tab
2. Click "Join DAO Now"
3. Confirm transaction in MetaMask
4. Receive 100 initial tokens

### Step 3: Submit a Website
1. Go to "Submit Website" tab
2. Enter website URL
3. Click "Submit Proposal"
4. Confirm transaction

### Step 4: Vote on Proposals
1. Go to "All Proposals" tab
2. View all submitted websites
3. Click vote button (Scam, High Risk, Normal, Safe)
4. Earn 10 tokens per vote

### Step 5: Finalize Proposals
- When a proposal has 3+ votes, "Finalize Proposal" button appears
- Click to process and determine final status
- Proposer earns 20 tokens

## MetaMask Configuration

### Add Ganache Network
1. Open MetaMask
2. Click network dropdown → "Add Network"
3. Enter details:
   - **Network Name**: Ganache Local
   - **RPC URL**: http://127.0.0.1:8545
   - **Chain ID**: 1337
   - **Currency Symbol**: ETH

### Import Ganache Account
1. Copy private key from Ganache
2. MetaMask → Account icon → "Import Account"
3. Paste private key

## File Structure
```
frontend/
├── index.html          # Main HTML structure
├── styles.css          # Styling and animations
├── app.js              # Web3 logic and interactions
├── contract_data.json  # Contract address and ABI
└── README.md           # This file
```

## Features Breakdown

### Dashboard Stats
- **Total Proposals**: Number of websites submitted
- **DAO Members**: Your membership status
- **Your Tokens**: Current token balance

### Proposal Card
- **Status Badge**: Visual indicator (Pending/Scam/High Risk/Normal/Safe)
- **Vote Counts**: Real-time vote distribution
- **Voting Buttons**: One-click voting interface
- **Finalize Button**: Appears when threshold is met

### Notifications
- **Toast Messages**: Success, error, and info notifications
- **Loading Overlay**: Transaction processing indicator
- **Real-time Updates**: Auto-refresh after transactions

## Troubleshooting

### "Please install MetaMask"
- Install MetaMask browser extension
- Refresh the page

### "Failed to connect wallet"
- Ensure MetaMask is unlocked
- Check if Ganache is running
- Verify network settings in MetaMask

### "Failed to load contract data"
- Ensure `contract_data.json` exists
- Run `python scripts/deploy.py` from project root
- Refresh the page

### Transactions Failing
- Check if you're a DAO member (join first)
- Ensure sufficient ETH in account
- Verify Ganache is running
- Check MetaMask network (should be Ganache)

### "Not a member" Error
- Go to "Join DAO" tab
- Click "Join DAO Now"
- Wait for transaction confirmation

## Technology Stack

- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS Grid and Flexbox
- **JavaScript (ES6+)**: Async/await, modules
- **Web3.js**: Ethereum blockchain interaction
- **Google Fonts**: Inter font family

## Browser Support

- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Brave
- ⚠️ Safari (Limited Web3 support)

## Security Notes

⚠️ **Development Only**: This frontend is for local development and educational purposes.

- Never use real private keys
- Only connect to Ganache (local blockchain)
- Don't deploy with production credentials

## Next Steps

### Enhancements You Can Add:
1. **Proposal History**: Show past proposals with filters
2. **Member Leaderboard**: Top voters and contributors
3. **Proposal Comments**: Discussion threads
4. **Time-based Voting**: Voting periods with countdown
5. **Advanced Stats**: Charts and analytics
6. **Export Data**: Download proposal history
7. **Dark/Light Theme Toggle**: User preference
8. **Multi-language Support**: i18n integration

## License

This project is for educational purposes as part of DS441 coursework.
