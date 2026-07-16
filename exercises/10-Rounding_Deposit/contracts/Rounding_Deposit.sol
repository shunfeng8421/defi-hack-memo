// Exercise 10: 存款舍入攻击
// Pattern: 存款舍入攻击 | Difficulty: ⭐⭐

contract VulnerableLending {
    function deposit(uint256 amount) external returns (uint256 shares) {
        shares = (amount * totalSupply) / totalAssets; // ⚠️ Rounds down
        // Attacker: deposit(1) when totalSupply=1000, totalAssets=1001
        // shares = 1*1000/1001 = 0 — free deposit!
    }
    uint256 totalSupply = 1000; uint256 totalAssets = 1001;
}