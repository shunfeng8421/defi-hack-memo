// Exercise: 预言机过期未检查
// Difficulty: ⭐⭐
contract VulnerableChainlink { function getPrice() external view returns (int) { (,int p,,uint updatedAt,) = feed.latestRoundData(); /* ⚠️ updatedAt never checked — could be hours stale */ return p; }}