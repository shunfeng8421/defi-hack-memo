// Exercise 18: 闪贷铸币膨胀
// Pattern: 闪贷铸币膨胀 | Difficulty: ⭐⭐⭐

contract VulnerableStablecoin {
    function mintWithCollateral(uint256 collateral) external {
        uint256 price = getSpotPrice(); // ⚠️ Flash-loan manipulable
        uint256 toMint = (collateral * price) / 1e18;
        _mint(msg.sender, toMint);
    }
}