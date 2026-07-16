// Exercise: 批量转账DoS
// Difficulty: ⭐⭐
contract VulnerableBatch { function batch(address[] calldata to, uint256[] calldata amounts) external { for(uint i=0; i<to.length; i++) token.transfer(to[i], amounts[i]); /* ⚠️ One failing transfer = entire batch reverts */ }}