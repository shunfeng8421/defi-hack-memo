// Exercise: 手续费覆盖
// Difficulty: ⭐⭐
contract VulnerableFees { uint256 feeBps; function setFee(uint256 bps) external onlyOwner { feeBps = bps; /* ⚠️ Can be changed mid-swap — sandwich attack */ }}