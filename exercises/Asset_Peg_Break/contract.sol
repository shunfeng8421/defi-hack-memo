// Exercise: 资产锚定破裂
// Difficulty: ⭐⭐⭐
contract StableSwap { function swap(uint a) external returns (uint) { return a * peg / 1e18; /* ⚠️ No mechanism to restore peg after deviation */ }}