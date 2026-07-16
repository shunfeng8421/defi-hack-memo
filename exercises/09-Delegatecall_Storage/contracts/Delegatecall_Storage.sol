// Exercise 09: delegatecall存储碰撞
// Pattern: delegatecall存储碰撞 | Difficulty: ⭐⭐

contract Proxy {
    address public impl;
    uint256 public value; // slot 1
    function upgrade(address _impl) external {
        impl = _impl;
        // ⚠️ No storage gap — new impl might overlap value slot
    }
    fallback() external { (bool ok,) = impl.delegatecall(msg.data); require(ok); }
}