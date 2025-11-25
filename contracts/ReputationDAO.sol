// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ReputationDAO {
    enum Reputation { Scam, HighRisk, Normal, Safe }
    enum Role { Member, Moderator, Admin }
    
    struct Proposal {
        uint id;
        string websiteUrl;
        address proposer;
        uint startTime;
        bool processed;
        bool active;
        mapping(uint8 => uint) voteCounts;
        Reputation finalStatus;
    }

    struct Member {
        bool isMember;
        uint tokens;
        Role role;
        uint joinedAt;
        uint proposalsSubmitted;
        uint votesCount;
        mapping(uint => bool) hasVoted;
    }

    address public admin;
    mapping(address => Member) public members;
    address[] public memberAddresses;
    Proposal[] public proposals;
    uint public proposalCount;
    uint public totalMembers;
    
    uint public constant REWARD_AMOUNT = 10;
    uint public constant VOTE_THRESHOLD = 3;

    event MemberJoined(address member, uint timestamp);
    event MemberRoleChanged(address member, Role newRole);
    event MemberRemoved(address member);
    event ProposalCreated(uint id, string url, address proposer);
    event Voted(uint proposalId, address voter, uint8 option);
    event ProposalProcessed(uint id, Reputation status);
    event ProposalDeactivated(uint id);

    modifier onlyMember() {
        require(members[msg.sender].isMember, "Not a member");
        _;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin || members[msg.sender].role == Role.Admin, "Not an admin");
        _;
    }

    modifier onlyModerator() {
        require(
            msg.sender == admin || 
            members[msg.sender].role == Role.Admin || 
            members[msg.sender].role == Role.Moderator, 
            "Not a moderator"
        );
        _;
    }

    constructor() {
        admin = msg.sender;
        members[msg.sender].isMember = true;
        members[msg.sender].tokens = 1000;
        members[msg.sender].role = Role.Admin;
        members[msg.sender].joinedAt = block.timestamp;
        memberAddresses.push(msg.sender);
        totalMembers = 1;
    }

    function joinDAO() external {
        require(!members[msg.sender].isMember, "Already a member");
        members[msg.sender].isMember = true;
        members[msg.sender].tokens = 100;
        members[msg.sender].role = Role.Member;
        members[msg.sender].joinedAt = block.timestamp;
        memberAddresses.push(msg.sender);
        totalMembers++;
        emit MemberJoined(msg.sender, block.timestamp);
    }

    function submitWebsite(string calldata _url) external onlyMember {
        Proposal storage newProposal = proposals.push();
        newProposal.id = proposalCount;
        newProposal.websiteUrl = _url;
        newProposal.proposer = msg.sender;
        newProposal.startTime = block.timestamp;
        newProposal.processed = false;
        newProposal.active = true;
        
        members[msg.sender].proposalsSubmitted++;
        proposalCount++;
        emit ProposalCreated(newProposal.id, _url, msg.sender);
    }

    function vote(uint _proposalId, uint8 _option) external onlyMember {
        require(_proposalId < proposalCount, "Invalid proposal ID");
        require(_option <= 3, "Invalid option");
        require(!members[msg.sender].hasVoted[_proposalId], "Already voted");
        
        Proposal storage p = proposals[_proposalId];
        require(!p.processed, "Proposal already processed");
        require(p.active, "Proposal is not active");

        p.voteCounts[_option]++;
        members[msg.sender].hasVoted[_proposalId] = true;
        members[msg.sender].tokens += REWARD_AMOUNT;
        members[msg.sender].votesCount++;
        
        emit Voted(_proposalId, msg.sender, _option);
    }

    function processProposal(uint _proposalId) external {
        require(_proposalId < proposalCount, "Invalid proposal ID");
        Proposal storage p = proposals[_proposalId];
        require(!p.processed, "Already processed");
        require(p.active, "Proposal is not active");
        
        uint totalVotes = p.voteCounts[0] + p.voteCounts[1] + p.voteCounts[2] + p.voteCounts[3];
        require(totalVotes >= VOTE_THRESHOLD, "Not enough votes to finalize");

        uint8 winner = 0;
        uint maxVotes = 0;
        for (uint8 i = 0; i <= 3; i++) {
            if (p.voteCounts[i] > maxVotes) {
                maxVotes = p.voteCounts[i];
                winner = i;
            }
        }
        
        p.finalStatus = Reputation(winner);
        p.processed = true;
        
        members[p.proposer].tokens += REWARD_AMOUNT * 2;
        
        emit ProposalProcessed(_proposalId, p.finalStatus);
    }
    
    // Admin Functions
    function setMemberRole(address _member, Role _role) external onlyAdmin {
        require(members[_member].isMember, "Not a member");
        members[_member].role = _role;
        emit MemberRoleChanged(_member, _role);
    }

    function removeMember(address _member) external onlyAdmin {
        require(members[_member].isMember, "Not a member");
        require(_member != admin, "Cannot remove admin");
        members[_member].isMember = false;
        totalMembers--;
        emit MemberRemoved(_member);
    }

    function deactivateProposal(uint _proposalId) external onlyModerator {
        require(_proposalId < proposalCount, "Invalid proposal ID");
        Proposal storage p = proposals[_proposalId];
        require(!p.processed, "Already processed");
        p.active = false;
        emit ProposalDeactivated(_proposalId);
    }

    function grantTokens(address _member, uint _amount) external onlyAdmin {
        require(members[_member].isMember, "Not a member");
        members[_member].tokens += _amount;
    }

    // View Functions
    function getProposalVotes(uint _proposalId) external view returns (uint, uint, uint, uint) {
        Proposal storage p = proposals[_proposalId];
        return (p.voteCounts[0], p.voteCounts[1], p.voteCounts[2], p.voteCounts[3]);
    }

    function getMemberInfo(address _member) external view returns (
        bool isMember,
        uint tokens,
        Role role,
        uint joinedAt,
        uint proposalsSubmitted,
        uint votesCount
    ) {
        Member storage m = members[_member];
        return (
            m.isMember,
            m.tokens,
            m.role,
            m.joinedAt,
            m.proposalsSubmitted,
            m.votesCount
        );
    }

    function getAllMembers() external view returns (address[] memory) {
        return memberAddresses;
    }

    function getMemberCount() external view returns (uint) {
        return totalMembers;
    }

    function isProposalActive(uint _proposalId) external view returns (bool) {
        require(_proposalId < proposalCount, "Invalid proposal ID");
        return proposals[_proposalId].active;
    }
}
