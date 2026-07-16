// Exercise 13: 初始化缺失
// Pattern: 初始化缺失 | Difficulty: ⭐⭐⭐

contract VulnerableProxy {
    bool public initialized;
    function initialize() external {
        // ⚠️ No initializer modifier — can be called multiple times
        // Attacker calls initialize after deploy to take ownership
        owner = msg.sender;
        initialized = true;
    }
    address public owner;
}