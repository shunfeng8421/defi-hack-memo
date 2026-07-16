// Exercise: 奖励率调整
// Difficulty: ⭐⭐
contract VulnerableReward { uint256 public rate; function setRate(uint256 r) external onlyOwner { rate=r; /* ⚠️ No timelock — owner can rug rewards */ }}