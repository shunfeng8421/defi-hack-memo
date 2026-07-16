// Exercise 04: Flash Loan Governance — ⭐⭐⭐
// Pattern #11: Flash Loan + Governance Attack
// 04-Contracts/GovernanceVault.sol + exploit inline

// 05: Precision Loss — ⭐
// Pattern #46: Division before multiplication
contract TokenSwap05 {
    function swapTokenForETH(uint256 tokenAmount) external returns (uint256) {
        uint256 rate = getRate(); // e.g. 0.95 ETH per token
        // VULNERABLE: division first causes truncation
        uint256 ethOut = (tokenAmount / 100) * rate; // ⚠️ 199/100=1, 1*rate=0.95
        // FIX: Multiply first
        // uint256 ethOut = (tokenAmount * rate) / 100; // 199*95/100=189.05
        return ethOut;
    }
    function getRate() internal pure returns (uint256) { return 95; }
}
