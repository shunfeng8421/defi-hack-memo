// Exercise: 硬编码gas
// Difficulty: ⭐
contract VulnerableTransfer { function send(address to) external { payable(to).transfer(msg.value); /* ⚠️ 2300 gas limit — breaks with complex fallbacks */ }}