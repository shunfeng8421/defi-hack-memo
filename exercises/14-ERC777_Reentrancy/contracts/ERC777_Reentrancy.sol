// Exercise 14: ERC777回调重入
// Pattern: ERC777回调重入 | Difficulty: ⭐⭐⭐

contract VulnerableVault {
    mapping(address => uint256) public shares;
    function redeem(uint256 amount) external {
        require(shares[msg.sender] >= amount);
        IERC777(token).send(msg.sender, amount, ""); // ⚠️ ERC777 callback BEFORE burn
        shares[msg.sender] -= amount; // Too late — reentrant call already happened
    }
}