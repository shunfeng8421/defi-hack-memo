// Exercise: 任意call注入
// Difficulty: ⭐⭐⭐
contract VulnerableRouter { function execute(address target, bytes calldata data) external { target.call(data); /* ⚠️ target can be ANY address — unlimited exploit surface */ }}