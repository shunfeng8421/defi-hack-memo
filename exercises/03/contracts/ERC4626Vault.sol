// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/// Exercise 03: ERC-4626 Inflation — ⭐⭐
/// Pattern #5: Deposit Donation Inflation

contract VulnerableERC4626 {
    uint256 public totalAssets;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    
    // VULNERABLE: 1:1 for first depositor, no dead shares
    function deposit(uint256 assets) external {
        uint256 shares;
        if (totalSupply == 0) {
            shares = assets; // 1:1 for first depositor ⚠️
        } else {
            shares = (assets * totalSupply) / totalAssets; // ⚠️ integer division
            require(shares > 0, "zero shares"); // Only protection
        }
        balanceOf[msg.sender] += shares;
        totalSupply += shares;
        totalAssets += assets;
        IERC20(asset).transferFrom(msg.sender, address(this), assets);
    }
    
    function redeem(uint256 shares) external {
        require(balanceOf[msg.sender] >= shares);
        uint256 assets = (shares * totalAssets) / totalSupply;
        balanceOf[msg.sender] -= shares;
        totalSupply -= shares;
        totalAssets -= assets;
        IERC20(asset).transfer(msg.sender, assets);
    }
    
    address public asset;
    constructor(address _asset) { asset = _asset; }
}

// EXPLOIT
// 1. deposit(1) → 1 share, totalAssets=1
// 2. Direct transfer 1000 tokens to vault → totalAssets=1001, no shares minted
// 3. Victim: deposit(1000) → (1000*1)/1001 = 0 shares → REVERT
// 4. Attacker: redeem(1) → (1*1001)/1 = 1001 tokens

// FIX: Mint dead shares on init, or enforce minDeposit
interface IERC20 {
    function transferFrom(address,address,uint256) external returns(bool);
    function transfer(address,uint256) external returns(bool);
}
