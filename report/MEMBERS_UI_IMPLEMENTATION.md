# Members UI Implementation Guide

## Overview
This guide explains how to add member names and a Members UI tab to your DAO system.

## ✅ What's Been Done

### 1. Smart Contract Updates
The `ReputationDAO.sol` contract has been updated with the following changes:

#### Added Name Field to Member Struct
```solidity
struct Member {
    bool isMember;
    uint tokens;
    Role role;
    uint joinedAt;
    uint proposalsSubmitted;
    uint votesCount;
    string name;  // ← NEW
    mapping(uint => bool) hasVoted;
}
```

#### Updated joinDAO Function
```solidity
function joinDAO(string calldata _name) external {
    require(!members[msg.sender].isMember, "Already a member");
    require(bytes(_name).length > 0 && bytes(_name).length <= 50, "Name must be 1-50 characters");
    members[msg.sender].isMember = true;
    members[msg.sender].tokens = 100;
    members[msg.sender].role = Role.Member;
    members[msg.sender].joinedAt = block.timestamp;
    members[msg.sender].name = _name;  // ← NEW
    memberAddresses.push(msg.sender);
    totalMembers++;
    emit MemberJoined(msg.sender, block.timestamp);
}
```

#### Updated getMemberInfo Function
```solidity
function getMemberInfo(address _member) external view returns (
    bool isMember,
    uint tokens,
    Role role,
    uint joinedAt,
    uint proposalsSubmitted,
    uint votesCount,
    string memory name  // ← NEW
) {
    Member storage m = members[_member];
    return (
        m.isMember,
        m.tokens,
        m.role,
        m.joinedAt,
        m.proposalsSubmitted,
        m.votesCount,
        m.name  // ← NEW
    );
}
```

#### Updated Constructor
```solidity
constructor() {
    admin = msg.sender;
    members[msg.sender].isMember = true;
    members[msg.sender].tokens = 1000;
    members[msg.sender].role = Role.Admin;
    members[msg.sender].joinedAt = block.timestamp;
    members[msg.sender].name = "Admin";  // ← NEW
    memberAddresses.push(msg.sender);
    totalMembers = 1;
}
```

## 📝 What Needs to Be Done

### Step 1: Redeploy the Contract
Since we've modified the contract, you need to redeploy it:

```powershell
# Activate virtual environment
.\.venv\Scripts\activate

# Deploy the updated contract
python scripts\deploy.py
```

### Step 2: Update Frontend HTML

Add a name input field to the Join DAO form in `frontend/index.html`.

Find this section (around line 217):
```html
<button id="joinDAOBtn" class="btn btn-primary btn-large">
    Join DAO Now
</button>
```

Replace it with:
```html
<form id="joinDAOForm" class="form" style="max-width: 400px; margin: 2rem auto 0;">
    <div class="form-group">
        <label for="memberName">Your Display Name</label>
        <input type="text" id="memberName" placeholder="Enter your name (1-50 characters)" 
               minlength="1" maxlength="50" required>
    </div>
    <button id="joinDAOBtn" type="submit" class="btn btn-primary btn-large">
        Join DAO Now
    </button>
</form>
```

### Step 3: Update Frontend JavaScript

Update `frontend/app.js` with the following changes:

#### 3.1 Update joinDAO Function

Find the `joinDAO` function (around line 342) and update it:

```javascript
// Join DAO
async function joinDAO(event) {
    event.preventDefault();  // Prevent form submission
    
    if (!contract || !currentAccount) {
        showToast('Please connect your wallet first', 'error');
        return;
    }

    // Get the name from the input field
    const nameInput = document.getElementById('memberName');
    const name = nameInput.value.trim();

    if (!name || name.length < 1 || name.length > 50) {
        showToast('Please enter a valid name (1-50 characters)', 'error');
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

        const tx = await contract.methods.joinDAO(name).send({
            from: currentAccount
        });

        showLoading(false);
        showToast('Successfully joined the DAO! You received 100 tokens.', 'success');

        nameInput.value = '';  // Clear the input
        await loadDashboard();

    } catch (error) {
        showLoading(false);
        console.error('Join DAO error:', error);

        if (error.message.includes('Already a member')) {
            showToast('You are already a DAO member', 'info');
        } else {
            showToast('Failed to join DAO', 'error');
        }
    }
}
```

#### 3.2 Add loadMembers Function

Add this new function to load and display all members:

```javascript
// Load all members
async function loadMembers() {
    if (!contract) return;

    try {
        const membersList = document.getElementById('membersList');
        membersList.innerHTML = '';

        // Get all member addresses
        const memberAddresses = await contract.methods.getAllMembers().call();

        if (memberAddresses.length === 0) {
            membersList.innerHTML = `
                <div class="empty-state">
                    <svg width="80" height="80" viewBox="0 0 80 80" fill="currentColor" opacity="0.3">
                        <path d="M40 20a10 10 0 100 20 10 10 0 000-20zm0 30c-13.3 0-24 5.4-24 12v6h48v-6c0-6.6-10.7-12-24-12z"/>
                    </svg>
                    <h3>No members yet</h3>
                    <p>Be the first to join the DAO!</p>
                </div>
            `;
            return;
        }

        // Load each member's info
        for (let address of memberAddresses) {
            const memberInfo = await contract.methods.getMemberInfo(address).call();
            const memberCard = createMemberCard(address, memberInfo);
            membersList.appendChild(memberCard);
        }

    } catch (error) {
        console.error('Load members error:', error);
        showToast('Failed to load members', 'error');
    }
}

// Create member card element
function createMemberCard(address, memberInfo) {
    const card = document.createElement('div');
    card.className = 'member-card';

    const roleNames = ['Member', 'Moderator', 'Admin'];
    const roleName = roleNames[memberInfo.role];
    const roleClass = roleName.toLowerCase();

    // Format joined date
    const joinedDate = new Date(parseInt(memberInfo.joinedAt) * 1000).toLocaleDateString();

    card.innerHTML = `
        <div class="member-header">
            <div class="member-avatar">
                <svg width="40" height="40" viewBox="0 0 40 40" fill="currentColor">
                    <circle cx="20" cy="15" r="8" opacity="0.8"/>
                    <path d="M20 25c-8 0-15 4-15 9v4h30v-4c0-5-7-9-15-9z" opacity="0.6"/>
                </svg>
            </div>
            <div class="member-info">
                <div class="member-name">${memberInfo.name || 'Anonymous'}</div>
                <div class="member-address">${address.substring(0, 6)}...${address.substring(38)}</div>
            </div>
            <span class="member-role ${roleClass}">${roleName}</span>
        </div>
        <div class="member-stats">
            <div class="member-stat">
                <div class="member-stat-label">Tokens</div>
                <div class="member-stat-value">${memberInfo.tokens}</div>
            </div>
            <div class="member-stat">
                <div class="member-stat-label">Proposals</div>
                <div class="member-stat-value">${memberInfo.proposalsSubmitted}</div>
            </div>
            <div class="member-stat">
                <div class="member-stat-label">Votes</div>
                <div class="member-stat-value">${memberInfo.votesCount}</div>
            </div>
            <div class="member-stat">
                <div class="member-stat-label">Joined</div>
                <div class="member-stat-value">${joinedDate}</div>
            </div>
        </div>
    `;

    return card;
}
```

#### 3.3 Update setupEventListeners Function

Find the `setupEventListeners` function and update the Join DAO button listener:

```javascript
// Change from:
document.getElementById('joinDAOBtn').addEventListener('click', joinDAO);

// To:
document.getElementById('joinDAOForm').addEventListener('submit', joinDAO);
```

Also add member search functionality:

```javascript
// Search functionality for members
const searchMembers = document.getElementById('searchMembers');
if (searchMembers) {
    searchMembers.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase().trim();
        const memberCards = document.querySelectorAll('.member-card');

        memberCards.forEach(card => {
            const name = card.querySelector('.member-name')?.textContent.toLowerCase() || '';
            const address = card.querySelector('.member-address')?.textContent.toLowerCase() || '';

            if (name.includes(searchTerm) || address.includes(searchTerm) || searchTerm === '') {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
}
```

#### 3.4 Update loadDashboard Function

Add a call to `loadMembers()` in the `loadDashboard` function:

```javascript
async function loadDashboard() {
    if (!contract || !currentAccount) return;

    try {
        // ... existing code ...

        // Load proposals
        await loadProposals();
        
        // Load members (NEW)
        await loadMembers();

    } catch (error) {
        console.error('Dashboard load error:', error);
    }
}
```

### Step 4: Add CSS Styles

Add these styles to `frontend/styles.css`:

```css
/* Member Cards */
.members-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
}

.member-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.member-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
    border-color: var(--primary);
}

.member-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.member-avatar {
    width: 50px;
    height: 50px;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
}

.member-info {
    flex: 1;
}

.member-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}

.member-address {
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-family: 'Courier New', monospace;
}

.member-role {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.member-role.admin {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
}

.member-role.moderator {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
}

.member-role.member {
    background: var(--bg-secondary);
    color: var(--text-secondary);
}

.member-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color);
}

.member-stat {
    text-align: center;
}

.member-stat-label {
    font-size: 0.75rem;
    color: var(--text-secondary);
    margin-bottom: 0.25rem;
}

.member-stat-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--primary);
}
```

## 🚀 Deployment Steps

1. **Redeploy the Contract:**
   ```powershell
   .\.venv\Scripts\activate
   python scripts\deploy.py
   ```

2. **Update HTML File:**
   - Add the name input form to the Join DAO section

3. **Update JavaScript File:**
   - Update `joinDAO` function
   - Add `loadMembers` and `createMemberCard` functions
   - Update `setupEventListeners`
   - Update `loadDashboard`

4. **Update CSS File:**
   - Add member card styles

5. **Test the Application:**
   - Start the frontend server: `python serve_frontend.py`
   - Open http://localhost:8000
   - Connect your wallet
   - Join the DAO with a name
   - Check the Members tab

## 📸 Expected Result

The Members tab will display:
- Member avatar (generated icon)
- Member name (from the contract)
- Wallet address (shortened)
- Role badge (Admin/Moderator/Member)
- Statistics: Tokens, Proposals, Votes, Joined Date
- Search functionality to filter members

## 🎯 Benefits

1. **Personalization:** Members can set display names instead of just showing addresses
2. **Better UX:** Easier to identify and interact with other members
3. **Transparency:** View all DAO members and their activity at a glance
4. **Search:** Quickly find specific members by name or address

## ⚠️ Important Notes

- The contract MUST be redeployed for these changes to take effect
- Existing members from the old contract won't have names (they'll show as "Anonymous")
- The admin account automatically gets the name "Admin"
- Names are limited to 1-50 characters
- Names are stored on-chain and cannot be changed after joining

## 🔧 Troubleshooting

**Issue:** "Already a member" error when trying to join
- **Solution:** You're already a member of the DAO. The Join DAO button should be hidden for existing members.

**Issue:** Members list is empty
- **Solution:** Make sure the contract is deployed and at least one member has joined.

**Issue:** Name not showing
- **Solution:** Ensure you redeployed the contract after making the changes. Old contracts don't have the name field.

---

**Status:** Contract updated ✅ | Frontend updates needed ⏳
