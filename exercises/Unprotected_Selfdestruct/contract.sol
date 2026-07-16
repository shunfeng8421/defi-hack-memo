// Exercise: 无保护的销毁
// Difficulty: ⭐⭐
contract VulnerableKill { function kill() external { selfdestruct(payable(msg.sender)); /* ⚠️ No access control — anyone can destroy */ }}