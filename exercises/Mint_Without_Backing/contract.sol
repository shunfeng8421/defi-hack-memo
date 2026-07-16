// Exercise: 无储备铸币
// Difficulty: ⭐⭐⭐
contract VulnerableMint { function mint(address to, uint amount) external onlyOwner { _mint(to, amount); /* ⚠️ No backing collateral required */ }}