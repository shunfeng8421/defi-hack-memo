// Exercise: TWAP窗口过短
// Difficulty: ⭐⭐
contract VulnerableTWAP { function getPrice() external view returns (uint256) { return (cumulativeNow - cumulativeLast) / 10 minutes; /* ⚠️ 10min TWAP still manipulable via multi-block */ }}