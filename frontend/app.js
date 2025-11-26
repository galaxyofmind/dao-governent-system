// DAO Governance DApp
let web3;
let contract;
let currentAccount;
let contractData;

// Ganache network configuration
const GANACHE_CHAIN_ID = '0x539'; // 1337 in hex
const GANACHE_NETWORK = {
    chainId: GANACHE_CHAIN_ID,
    chainName: 'Ganache Local',
    rpcUrls: ['http://127.0.0.1:8545'],
    nativeCurrency: {
        name: 'Ethereum',
        symbol: 'ETH',
        decimals: 18
    }
};

// Initialize the app
async function init() {
    try {
        // Load contract data
        const response = await fetch('contract_data.json');
        contractData = await response.json();

        // Setup event listeners
        setupEventListeners();

        // Check if MetaMask is installed
        if (typeof window.ethereum !== 'undefined') {
            console.log('MetaMask is installed!');
        } else {
            showToast('Please install MetaMask to use this DApp', 'error');
        }
    } catch (error) {
        console.error('Initialization error:', error);
        showToast('Failed to load contract data', 'error');
    }
}

// Connect wallet
async function connectWallet() {
    try {
        if (typeof window.ethereum === 'undefined') {
            showToast('Please install MetaMask', 'error');
            return;
        }

        // Request account access
        const accounts = await window.ethereum.request({
            method: 'eth_requestAccounts'
        });

        currentAccount = accounts[0];

        // Initialize Web3
        web3 = new Web3(window.ethereum);

        // Check and switch to Ganache network
        await ensureGanacheNetwork();

        // Initialize contract
        contract = new web3.eth.Contract(contractData.abi, contractData.address);

        // Update UI
        updateWalletUI();
        await loadDashboard();

        showToast('Wallet connected successfully!', 'success');

        // Listen for account changes
        window.ethereum.on('accountsChanged', handleAccountsChanged);

        // Listen for network changes
        window.ethereum.on('chainChanged', handleChainChanged);

    } catch (error) {
        console.error('Connection error:', error);
        showToast('Failed to connect wallet', 'error');
    }
}

// Disconnect wallet
function disconnectWallet() {
    currentAccount = null;
    contract = null;
    web3 = null;
    updateWalletUI();
    showToast('Wallet disconnected', 'info');
}

// Switch wallet
async function switchWallet() {
    try {
        // Request to switch accounts
        const accounts = await window.ethereum.request({
            method: 'wallet_requestPermissions',
            params: [{
                eth_accounts: {}
            }]
        });

        // Reconnect with new account
        await connectWallet();

    } catch (error) {
        console.error('Switch wallet error:', error);
        showToast('Failed to switch wallet', 'error');
    }
}

// Ensure user is on Ganache network
async function ensureGanacheNetwork() {
    try {
        const chainId = await window.ethereum.request({ method: 'eth_chainId' });

        if (chainId !== GANACHE_CHAIN_ID) {
            try {
                // Try to switch to Ganache
                await window.ethereum.request({
                    method: 'wallet_switchEthereumChain',
                    params: [{ chainId: GANACHE_CHAIN_ID }],
                });
                showToast('Switched to Ganache network', 'success');
            } catch (switchError) {
                // Network doesn't exist, add it
                if (switchError.code === 4902) {
                    try {
                        await window.ethereum.request({
                            method: 'wallet_addEthereumChain',
                            params: [GANACHE_NETWORK],
                        });
                        showToast('Ganache network added and selected', 'success');
                    } catch (addError) {
                        throw new Error('Failed to add Ganache network');
                    }
                } else {
                    throw switchError;
                }
            }
        }
    } catch (error) {
        console.error('Network switch error:', error);
        showToast('Please switch to Ganache network (Chain ID: 1337)', 'error');
        throw error;
    }
}

// Handle chain changes
function handleChainChanged(chainId) {
    if (chainId !== GANACHE_CHAIN_ID) {
        showToast('Wrong network! Please switch to Ganache (Chain ID: 1337)', 'error');
        // Reload to reset state
        window.location.reload();
    } else {
        showToast('Connected to Ganache network', 'success');
        loadDashboard();
    }
}

// Handle account changes
function handleAccountsChanged(accounts) {
    if (accounts.length === 0) {
        // User disconnected
        disconnectWallet();
    } else {
        currentAccount = accounts[0];
        updateWalletUI();
        loadDashboard();
        showToast('Account switched', 'info');
    }
}

// Update wallet UI
function updateWalletUI() {
    const connectBtn = document.getElementById('connectWallet');
    const walletConnected = document.getElementById('walletConnected');
    const walletAddress = document.getElementById('walletAddress');

    if (currentAccount) {
        connectBtn.style.display = 'none';
        walletConnected.style.display = 'flex';
        walletAddress.textContent = `${currentAccount.substring(0, 6)}...${currentAccount.substring(38)}`;
    } else {
        connectBtn.style.display = 'block';
        walletConnected.style.display = 'none';
    }
}

// Load dashboard data
async function loadDashboard() {
    if (!contract || !currentAccount) return;

    try {
        // Get total proposals
        const proposalCount = await contract.methods.proposalCount().call();
        document.getElementById('totalProposals').textContent = proposalCount;

        // Get total members count
        try {
            const memberCount = await contract.methods.getMemberCount().call();
            document.getElementById('totalMembers').textContent = memberCount;
        } catch (error) {
            // Fallback: try totalMembers if getMemberCount doesn't exist
            try {
                const totalMembers = await contract.methods.totalMembers().call();
                document.getElementById('totalMembers').textContent = totalMembers;
            } catch (e) {
                console.log('Member count not available:', error);
                document.getElementById('totalMembers').textContent = '1+';
            }
        }

        // Get user tokens
        const member = await contract.methods.members(currentAccount).call();
        document.getElementById('tokenBalance').textContent = member.tokens;
        document.getElementById('userTokens').textContent = member.tokens;

        // Check if user is a member
        if (member.isMember) {
            document.getElementById('joinDAOBtn').style.display = 'none';
            document.getElementById('memberStatus').style.display = 'flex';
        } else {
            document.getElementById('joinDAOBtn').style.display = 'inline-flex';
            document.getElementById('memberStatus').style.display = 'none';
        }

        // Load proposals
        await loadProposals();

        // Load members
        await loadMembers();

    } catch (error) {
        console.error('Dashboard load error:', error);
    }
}

// Load all proposals
async function loadProposals() {
    if (!contract) return;

    try {
        const proposalCount = await contract.methods.proposalCount().call();
        const proposalsList = document.getElementById('proposalsList');
        proposalsList.innerHTML = '';

        if (proposalCount == 0) {
            proposalsList.innerHTML = `
                <div class="empty-state">
                    <svg width="80" height="80" viewBox="0 0 80 80" fill="currentColor" opacity="0.3">
                        <path d="M40 10L50 20L40 30L30 20L40 10Z"/>
                        <path d="M40 30L50 40L40 50L30 40L40 30Z" opacity="0.6"/>
                        <path d="M40 50L50 60L40 70L30 60L40 50Z" opacity="0.3"/>
                    </svg>
                    <h3>No proposals yet</h3>
                    <p>Be the first to submit a website for evaluation!</p>
                </div>
            `;
            return;
        }

        // Load each proposal
        for (let i = 0; i < proposalCount; i++) {
            const proposal = await contract.methods.proposals(i).call();
            const votes = await contract.methods.getProposalVotes(i).call();

            const proposalCard = createProposalCard(i, proposal, votes);
            proposalsList.appendChild(proposalCard);
        }

    } catch (error) {
        console.error('Load proposals error:', error);
        showToast('Failed to load proposals', 'error');
    }
}

// Create proposal card element
function createProposalCard(id, proposal, votes) {
    const card = document.createElement('div');
    card.className = 'proposal-card';

    const statusMap = ['Scam', 'HighRisk', 'Normal', 'Safe'];
    const statusClass = proposal.processed ?
        `status-${statusMap[proposal.finalStatus].toLowerCase()}` :
        'status-pending';
    const statusText = proposal.processed ?
        statusMap[proposal.finalStatus] :
        'Pending';

    const totalVotes = parseInt(votes[0]) + parseInt(votes[1]) + parseInt(votes[2]) + parseInt(votes[3]);

    card.innerHTML = `
        <div class="proposal-header">
            <span class="proposal-id">Proposal #${id}</span>
            <span class="proposal-status ${statusClass}">${statusText}</span>
        </div>
        <div class="proposal-url">
            <a href="${proposal.websiteUrl}" target="_blank" rel="noopener noreferrer">
                ${proposal.websiteUrl}
            </a>
        </div>
        <div class="proposal-meta">
            <span>Proposer: ${proposal.proposer.substring(0, 6)}...${proposal.proposer.substring(38)}</span>
            <span>Total Votes: ${totalVotes}</span>
        </div>
        <div class="vote-counts">
            <div class="vote-count">
                <div class="vote-count-label">Scam</div>
                <div class="vote-count-value" style="color: var(--danger);">${votes[0]}</div>
            </div>
            <div class="vote-count">
                <div class="vote-count-label">High Risk</div>
                <div class="vote-count-value" style="color: var(--warning);">${votes[1]}</div>
            </div>
            <div class="vote-count">
                <div class="vote-count-label">Normal</div>
                <div class="vote-count-value" style="color: var(--info);">${votes[2]}</div>
            </div>
            <div class="vote-count">
                <div class="vote-count-label">Safe</div>
                <div class="vote-count-value" style="color: var(--success);">${votes[3]}</div>
            </div>
        </div>
        ${!proposal.processed ? `
            <div class="voting-buttons">
                <button class="vote-btn scam" onclick="vote(${id}, 0)">Vote Scam</button>
                <button class="vote-btn highrisk" onclick="vote(${id}, 1)">Vote High Risk</button>
                <button class="vote-btn normal" onclick="vote(${id}, 2)">Vote Normal</button>
                <button class="vote-btn safe" onclick="vote(${id}, 3)">Vote Safe</button>
            </div>
            ${totalVotes >= 3 ? `
                <button class="btn btn-primary" style="margin-top: 1rem; width: 100%;" onclick="processProposal(${id})">
                    Finalize Proposal
                </button>
            ` : ''}
        ` : ''}
    `;

    return card;
}

// Join DAO
async function joinDAO() {
    if (!contract || !currentAccount) {
        showToast('Please connect your wallet first', 'error');
        return;
    }

    // Prompt for name (Required by contract)
    const name = prompt('Please enter your display name to join the DAO:');

    if (!name || name.trim().length === 0) {
        showToast('Name is required to join', 'error');
        return;
    }

    if (name.length > 50) {
        showToast('Name is too long (max 50 chars)', 'error');
        return;
    }

    try {
        await ensureGanacheNetwork();
        showLoading(true);

        // Send transaction with name
        await contract.methods.joinDAO(name).send({
            from: currentAccount
        });

        showLoading(false);
        showToast(`Welcome ${name}! You are now a DAO member.`, 'success');

        await loadDashboard();

    } catch (error) {
        showLoading(false);
        console.error('Join DAO error:', error);
        if (error.message.includes('Already a member')) {
            showToast('You are already a member', 'info');
        } else {
            showToast('Failed to join DAO', 'error');
        }
    }
}

// Load all members (Protected: Only for members)
async function loadMembers() {
    if (!contract || !currentAccount) return;

    const membersList = document.getElementById('membersList');
    if (!membersList) return;

    try {
        // Check permission first
        const memberInfo = await contract.methods.members(currentAccount).call();
        if (!memberInfo.isMember) {
            membersList.innerHTML = `
                <div class="empty-state">
                    <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 15v2m0 0v2m0-2h2m-2 0H10m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <h3>Access Denied</h3>
                    <p>Only DAO members can view the member list.</p>
                    <button onclick="switchTab('join')" class="btn btn-primary" style="margin-top: 1rem;">Join DAO</button>
                </div>
            `;
            return;
        }

        // Fetch members
        membersList.innerHTML = '<div class="loading">Loading members...</div>';

        const memberAddresses = await contract.methods.getAllMembers().call();
        membersList.innerHTML = ''; // Clear loading

        if (memberAddresses.length === 0) {
            membersList.innerHTML = '<div class="empty-state">No members found</div>';
            return;
        }

        for (const address of memberAddresses) {
            // Get detailed info including name
            const info = await contract.methods.getMemberInfo(address).call();

            const card = document.createElement('div');
            card.className = 'member-card';

            // Role badge style
            const roles = ['Member', 'Moderator', 'Admin'];
            const roleName = roles[info.role];
            const roleClass = roleName.toLowerCase();

            card.innerHTML = `
                <div class="member-header">
                    <div class="member-avatar">
                        <span>${info.name.charAt(0).toUpperCase()}</span>
                    </div>
                    <div class="member-info">
                        <div class="member-name">${info.name}</div>
                        <div class="member-address">${address.substring(0, 6)}...${address.substring(38)}</div>
                    </div>
                    <span class="member-role ${roleClass}">${roleName}</span>
                </div>
                <div class="member-stats">
                    <div class="stat">
                        <label>Tokens</label>
                        <span>${info.tokens}</span>
                    </div>
                    <div class="stat">
                        <label>Proposals</label>
                        <span>${info.proposalsSubmitted}</span>
                    </div>
                    <div class="stat">
                        <label>Votes</label>
                        <span>${info.votesCount}</span>
                    </div>
                </div>
            `;
            membersList.appendChild(card);
        }

    } catch (error) {
        console.error('Error loading members:', error);
        membersList.innerHTML = '<div class="error-state">Failed to load members</div>';
    }
}

// Submit website
async function submitWebsite(event) {
    event.preventDefault();

    if (!contract || !currentAccount) {
        showToast('Please connect your wallet first', 'error');
        return;
    }

    const urlInput = document.getElementById('websiteUrl');
    const url = urlInput.value.trim();

    if (!url) {
        showToast('Please enter a website URL', 'error');
        return;
    }

    // Ensure on Ganache network before transaction
    try {
        await ensureGanacheNetwork();
    } catch (error) {
        return;
    }

    try {
        showLoading(true);

        const tx = await contract.methods.submitWebsite(url).send({
            from: currentAccount
        });

        showLoading(false);
        showToast('Website submitted successfully!', 'success');

        urlInput.value = '';
        await loadDashboard();

        // Switch to proposals tab
        switchTab('proposals');

    } catch (error) {
        showLoading(false);
        console.error('Submit error:', error);

        if (error.message.includes('Not a member')) {
            showToast('You must join the DAO first', 'error');
        } else {
            showToast('Failed to submit website', 'error');
        }
    }
}

// Vote on proposal
async function vote(proposalId, option) {
    if (!contract || !currentAccount) {
        showToast('Please connect your wallet first', 'error');
        return;
    }

    const optionNames = ['Scam', 'High Risk', 'Normal', 'Safe'];

    // Ensure on Ganache network before transaction
    try {
        await ensureGanacheNetwork();
    } catch (error) {
        return;
    }

    try {
        showLoading(true);

        const tx = await contract.methods.vote(proposalId, option).send({
            from: currentAccount
        });

        showLoading(false);
        showToast(`Voted "${optionNames[option]}" successfully! You earned 10 tokens.`, 'success');

        await loadDashboard();

    } catch (error) {
        showLoading(false);
        console.error('Vote error:', error);

        if (error.message.includes('Already voted')) {
            showToast('You have already voted on this proposal', 'info');
        } else if (error.message.includes('Not a member')) {
            showToast('You must join the DAO first', 'error');
        } else {
            showToast('Failed to vote', 'error');
        }
    }
}

// Process proposal
async function processProposal(proposalId) {
    if (!contract || !currentAccount) {
        showToast('Please connect your wallet first', 'error');
        return;
    }

    // Ensure on Ganache network before transaction
    try {
        await ensureGanacheNetwork();
    } catch (error) {
        return;
    }

    try {
        showLoading(true);

        const tx = await contract.methods.processProposal(proposalId).send({
            from: currentAccount
        });

        showLoading(false);
        showToast('Proposal finalized successfully!', 'success');

        await loadDashboard();

    } catch (error) {
        showLoading(false);
        console.error('Process error:', error);

        if (error.message.includes('Not enough votes')) {
            showToast('Not enough votes to finalize (minimum 3 votes required)', 'info');
        } else if (error.message.includes('Already processed')) {
            showToast('This proposal has already been finalized', 'info');
        } else {
            showToast('Failed to finalize proposal', 'error');
        }
    }
}

// Setup event listeners
function setupEventListeners() {
    // Connect wallet button
    document.getElementById('connectWallet').addEventListener('click', connectWallet);

    // Join DAO button
    document.getElementById('joinDAOBtn').addEventListener('click', joinDAO);

    // Submit form
    document.getElementById('submitForm').addEventListener('submit', submitWebsite);

    // Tab switching
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.getAttribute('data-tab');
            switchTab(tabName);
        });
    });

    // Search functionality
    const searchInput = document.getElementById('searchProposals');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase().trim();
            const proposalCards = document.querySelectorAll('.proposal-card');

            proposalCards.forEach(card => {
                const url = card.querySelector('.proposal-url a')?.textContent.toLowerCase() || '';
                const proposalId = card.querySelector('.proposal-id')?.textContent.toLowerCase() || '';

                if (url.includes(searchTerm) || proposalId.includes(searchTerm) || searchTerm === '') {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });

            // Show "no results" message if all cards are hidden
            const visibleCards = Array.from(proposalCards).filter(card => card.style.display !== 'none');
            const proposalsList = document.getElementById('proposalsList');

            if (visibleCards.length === 0 && searchTerm !== '') {
                const existingMsg = proposalsList.querySelector('.no-results');
                if (!existingMsg) {
                    const noResults = document.createElement('div');
                    noResults.className = 'no-results empty-state';
                    noResults.innerHTML = `
                        <svg width="60" height="60" viewBox="0 0 24 24" fill="currentColor" opacity="0.3">
                            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/>
                        </svg>
                        <h3>No results found</h3>
                        <p>Try searching with a different term</p>
                    `;
                    proposalsList.appendChild(noResults);
                }
            } else {
                const existingMsg = proposalsList.querySelector('.no-results');
                if (existingMsg) existingMsg.remove();
            }
        });
    }
}

// Switch tabs
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

// Show toast notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" style="color: var(--success);"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
        error: '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" style="color: var(--danger);"><path d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
        info: '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" style="color: var(--info);"><path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
    };

    toast.innerHTML = `
        ${icons[type]}
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Show/hide loading overlay
function showLoading(show) {
    document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
}

// Initialize on page load
window.addEventListener('load', init);
