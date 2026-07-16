// Exercise 19: Rebase快照攻击
// Pattern: Rebase快照攻击 | Difficulty: ⭐⭐⭐

contract VulnerableRewards {
    mapping(address => uint256) public lastBalance;
    function claimRewards() external {
        uint256 current = balanceOf[msg.sender];
        // ⚠️ Uses current balance instead of snapshot
        uint256 reward = (current - lastBalance[msg.sender]) * rate;
        lastBalance[msg.sender] = current;
        token.transfer(msg.sender, reward);
    }
}