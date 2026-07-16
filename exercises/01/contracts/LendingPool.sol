// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Exercise 01: Flash Loan Price Oracle
/// @dev VULNERABLE: Uses Uniswap V2 spot price for token valuation
/// Pattern #1: Flash Loan + Price Oracle Manipulation
/// Difficulty: ⭐⭐

interface IUniswapV2Pair {
    function getReserves() external view returns (uint112 r0, uint112 r1, uint32);
    function token0() external view returns (address);
}

contract VulnerableLendingPool {
    IUniswapV2Pair public immutable pair;
    address public immutable TOKEN;   // e.g. DAI
    address public immutable OHM;     // e.g. OHM (the token being valued)
    
    mapping(address => uint256) public deposits;
    mapping(address => uint256) public borrows;
    
    constructor(address _pair, address _token, address _ohm) {
        pair = IUniswapV2Pair(_pair);
        TOKEN = _token;
        OHM = _ohm;
    }
    
    /// @notice Deposit collateral and borrow tokens
    function depositAndBorrow(uint256 collateralAmount, uint256 borrowAmount) external {
        // Transfer collateral in
        IERC20(OHM).transferFrom(msg.sender, address(this), collateralAmount);
        deposits[msg.sender] += collateralAmount;
        
        // Calculate borrow limit based on OHM price
        uint256 ohmPrice = getOHMPrice();  // ⚠️ SPOT PRICE!
        uint256 maxBorrow = (collateralAmount * ohmPrice) / 1e18;
        
        require(borrowAmount <= maxBorrow * 80 / 100, "Exceeds LTV"); // 80% LTV
        
        borrows[msg.sender] += borrowAmount;
        IERC20(TOKEN).transfer(msg.sender, borrowAmount);
    }
    
    /// @dev VULNERABLE: Uses instantaneous pool reserves for pricing
    function getOHMPrice() public view returns (uint256) {
        (uint112 r0, uint112 r1,) = pair.getReserves();
        // If OHM is token0, price = r1 / r0
        bool isToken0 = pair.token0() == OHM;
        if (isToken0) {
            return (uint256(r1) * 1e18) / uint256(r0);
        } else {
            return (uint256(r0) * 1e18) / uint256(r1);
        }
    }
    
    function getMaxBorrow(uint256 collateralAmount) external view returns (uint256) {
        return (collateralAmount * getOHMPrice()) / 1e18 * 80 / 100;
    }
}

interface IERC20 {
    function transferFrom(address, address, uint256) external returns (bool);
    function transfer(address, uint256) external returns (bool);
    function balanceOf(address) external view returns (uint256);
}
