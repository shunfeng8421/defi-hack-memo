// Exercise 08: 时间锁绕过
// Pattern: 时间锁绕过 | Difficulty: ⭐⭐⭐

contract VulnerableTimelock {
    uint256 public constant DELAY = 2 days;
    function execute(address target, bytes calldata data) external {
        require(queued[target][data] + DELAY < block.timestamp); // ⚠️ Uses < not <=
        // Edge: if queued at exactly T, executes at T+DELAY (not T+DELAY+1)
    }
}