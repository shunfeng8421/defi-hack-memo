// Exercise 12: 预言机过期
// Pattern: 预言机过期 | Difficulty: ⭐⭐

contract VulnerableOracle {
    function getPrice() external view returns (int256) {
        (, int256 price,,,) = AggregatorV3(feed).latestRoundData();
        // ⚠️ No staleness check — can use hours-old price
        return price;
    }
}