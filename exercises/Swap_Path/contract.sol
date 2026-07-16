// Exercise: 交易路径劫持
// Difficulty: ⭐⭐⭐
contract VulnerableAggregator { function swap(address[] calldata path, uint256 a) external { for(uint i; i<path.length-1; i++) { pair(path[i], path[i+1]).swap(a); /* ⚠️ No path validation — attacker can insert malicious pool */ }}