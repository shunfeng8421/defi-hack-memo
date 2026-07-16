// Exercise 20: 无界循环
// Pattern: 无界循环 | Difficulty: ⭐⭐

contract VulnerableBatch {
    function processBatch(address[] calldata users) external {
        for (uint i = 0; i < users.length; i++) {
            // ⚠️ No max length — can exceed block gas limit
            token.transfer(users[i], amount);
        }
    }
}