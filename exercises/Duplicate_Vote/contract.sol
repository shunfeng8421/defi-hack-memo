// Exercise: 重复投票
// Difficulty: ⭐⭐
contract VulnerableVote { mapping(uint=>mapping(address=>bool)) voted; function vote(uint pid) external { require(!voted[pid][msg.sender]); voted[pid][msg.sender]=true; /* OK */ votes[pid]++; /* ⚠️ But what if msg.sender has multiple delegates? */ }}