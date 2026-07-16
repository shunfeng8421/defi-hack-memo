// Exercise 15: CREATE2前置攻击
// Pattern: CREATE2前置攻击 | Difficulty: ⭐⭐⭐

contract VulnerableFactory {
    function deploy(bytes32 salt, bytes calldata code) external returns (address) {
        // ⚠️ No salt includes msg.sender — anyone can front-run
        return address(new Contract{salt: salt}(code));
    }
}