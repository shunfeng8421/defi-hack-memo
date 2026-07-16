// Exercise: 代理初始化前置
// Difficulty: ⭐⭐⭐
contract VulnerableProxy { bool init; function initialize(address owner) external { require(!init); init = true; owner=owner; /* ⚠️ Anyone can call initialize before deployer */ }}