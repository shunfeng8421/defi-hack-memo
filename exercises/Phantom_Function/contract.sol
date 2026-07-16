// Exercise: 幽灵函数
// Difficulty: ⭐⭐⭐
contract VulnerableFallback { fallback() external payable { /* Every call succeeds silently ⚠️ — funds can be permanently locked */ }}