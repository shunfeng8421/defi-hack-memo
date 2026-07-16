// Exercise: 存款永久锁定
// Difficulty: ⭐⭐
contract VulnerableLock { mapping(address=>uint) balances; function deposit() external payable { balances[msg.sender] += msg.value; } /* ⚠️ Missing withdraw function! */ }