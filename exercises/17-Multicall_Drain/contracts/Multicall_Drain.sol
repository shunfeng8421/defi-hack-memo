// Exercise 17: 多调用抽干
// Pattern: 多调用抽干 | Difficulty: ⭐⭐⭐

contract VulnerableMulticall {
    function multicall(bytes[] calldata data) external {
        for (uint i = 0; i < data.length; i++) {
            // ⚠️ Can call transferFrom if victim approved this contract
            address(this).call(data[i]);
        }
    }
}