// Exercise: 前置质押操纵
// Difficulty: ⭐⭐
contract VulnerableStaking { function stake(uint256 amount) external { uint256 reward = totalReward * amount / totalStaked; /* ⚠️ Front-run by depositing right before reward distribution */ }}