// Exercise: 手续费计算方向
// Difficulty: ⭐⭐
contract VulnerableFee { function swap(uint a) external returns (uint) { uint fee = a * feeBps / 10000; return a - fee; /* ⚠️ fee deducted BUT slipssage also applied — double fee */ }}