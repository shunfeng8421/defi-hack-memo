// Exercise 06: AMM储备不同步
// Pattern: AMM储备不同步 | Difficulty: ⭐⭐

contract VulnerableAMM {
    mapping(address => uint256) public balanceOf;
    uint256 public reserve0, reserve1;
    function swap(uint amountIn) external {
        uint out = (amountIn * reserve1) / reserve0;  // ⚠️ No balance validation
        // Doesn't check actual token balance
        reserve0 += amountIn;
        reserve1 -= out;
    }
}