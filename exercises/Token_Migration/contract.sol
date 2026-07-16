// Exercise: 代币迁移劫持
// Difficulty: ⭐⭐⭐
contract VulnerableMigration { function migrate(address old, uint256 amount) external { oldToken(old).burn(msg.sender, amount); /* ⚠️ No validation that old token is trusted */ newToken.mint(msg.sender, amount); }}