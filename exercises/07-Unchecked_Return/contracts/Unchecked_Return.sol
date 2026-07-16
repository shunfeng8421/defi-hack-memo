// Exercise 07: 未检查返回值
// Pattern: 未检查返回值 | Difficulty: ⭐

contract VulnerableToken {
    function transfer(address to, uint256 amount) external {
        IERC20(token).transferFrom(msg.sender, to, amount); // ⚠️ No return check
        // transfers can silently fail on some tokens (USDT)
    }
}