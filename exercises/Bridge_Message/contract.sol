// Exercise: 桥消息伪造
// Difficulty: ⭐⭐⭐
contract VulnerableBridge { function processMessage(bytes calldata msg) external { (address from, address to, uint256 amount) = abi.decode(msg, (address,address,uint256)); transfer(to,amount); /* ⚠️ No signature verification on message */ }}