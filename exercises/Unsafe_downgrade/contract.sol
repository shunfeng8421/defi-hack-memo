// Exercise: 不安全的降级cast
// Difficulty: ⭐⭐⭐
contract VulnerableCast { function process(uint256 a) external { uint128 b = uint128(a); /* ⚠️ Silent truncation — a may exceed uint128 */ }}