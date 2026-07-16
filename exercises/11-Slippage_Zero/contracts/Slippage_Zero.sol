// Exercise 11: 零滑点保护
// Pattern: 零滑点保护 | Difficulty: ⭐

contract VulnerableSwap {
    function swap(address token, uint256 amount) external {
        uint256 out = getAmountOut(amount);
        IUniswapRouter(router).swapExactTokensForTokens(
            amount, 0, path, msg.sender // ⚠️ minOut = 0 — sandwich target
        );
    }
}