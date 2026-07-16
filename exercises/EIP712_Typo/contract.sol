// Exercise: EIP712 TYPEHASH错误
// Difficulty: ⭐⭐⭐
contract VulnerableEIP712 { bytes32 constant TYPEHASH = keccak256(bytes('Transfer(address from,address to,uint256 amout)')); /* ⚠️ 'amout' typo — signatures from standard tools break */ }