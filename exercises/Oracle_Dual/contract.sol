// Exercise: 双预言机不一致
// Difficulty: ⭐⭐⭐
contract VulnerableDualOracle { function getPrice() external view returns (uint256) { uint256 p1 = oracle1.getPrice(); uint256 p2 = oracle2.getPrice(); return (p1+p2)/2; /* ⚠️ No discrepancy check — one oracle can be manipulated */ }}