// Exercise: 管理员放弃权限
// Difficulty: ⭐⭐
contract VulnerableOwnable { address public owner; function renounceOwnership() external onlyOwner { owner = address(0); /* ⚠️ Permanent lockout — no recovery */ }}