// Exercise: 清算机器人贿赂
// Difficulty: ⭐⭐⭐
contract VulnerableLiquidate { function liquidate(address u) external { uint256 reward = debt[u]*5/100; /* ⚠️ Flat 5% reward — MEV bot incentive */ transfer(msg.sender, reward); }}