// Exercise: 认领无截止
// Difficulty: ⭐⭐
contract VulnerableAirdrop { mapping(address=>uint) claimable; function claim() external { uint a = claimable[msg.sender]; delete claimable[msg.sender]; transfer(msg.sender, a); /* ⚠️ No deadline — funds lock if never claimed */ }}