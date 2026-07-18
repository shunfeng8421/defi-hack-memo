// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title AI Agent × DeFi Sandbox — 8 Attack Vectors Demo
/// @author Shiqiang Chen — July 2026
/// @dev 包含: Mock AMM, 借贷池, AI Agent, 以及全部8个攻击向量

// ═══════════════════════════════════════════════
// 组件1: Mock AMM (模拟 Uniswap V2)
// ═══════════════════════════════════════════════
contract MockAMM {
    uint256 public reserveToken;
    uint256 public reserveETH;
    
    constructor() payable {
        reserveToken = 1000 ether;
        reserveETH = 1000 ether;
    }
    
    function getSpotPrice() external view returns (uint256) {
        return (reserveETH * 1e18) / reserveToken;
    }
    
    function swapTokenForETH(uint256 amountIn) external returns (uint256) {
        uint256 amountOut = (amountIn * reserveETH) / (reserveToken + amountIn);
        reserveToken += amountIn;
        reserveETH -= amountOut;
        payable(msg.sender).transfer(amountOut);
        return amountOut;
    }
    
    function swapETHForToken() external payable returns (uint256) {
        uint256 amountOut = (msg.value * reserveToken) / (reserveETH + msg.value);
        reserveETH += msg.value;
        reserveToken -= amountOut;
        return amountOut;
    }

    receive() external payable {}
}

// ═══════════════════════════════════════════════
// 组件2: 借贷池 (模拟 Aave)
// ═══════════════════════════════════════════════
contract MockLendingPool {
    mapping(address => uint256) public deposits;
    mapping(address => uint256) public borrows;
    uint256 public interestRate = 5; // 5% APY
    
    function deposit() external payable {
        deposits[msg.sender] += msg.value;
    }
    
    /// ⚠️ VULNERABLE: 无 access control
    function borrow(uint256 amount) external {
        require(address(this).balance >= amount, "insufficient");
        borrows[msg.sender] += amount;
        payable(msg.sender).transfer(amount);
    }
    
    function getBorrowAPY() external view returns (uint256) {
        uint256 totalBorrowed = address(this).balance; // simplified
        uint256 totalDeposited = address(this).balance + 100 ether;
        return (totalBorrowed * interestRate * 100) / totalDeposited;
    }
}

// ═══════════════════════════════════════════════
// 组件3: AI Agent 钱包 — 自动管理 DeFi 仓位
// ═══════════════════════════════════════════════
contract AIAgentWallet {
    address public owner;
    MockAMM public amm;
    MockLendingPool public lending;
    
    constructor(address _amm, address _lending) {
        owner = msg.sender;
        amm = MockAMM(_amm);
        lending = MockLendingPool(_lending);
    }
    
    /// ⚠️ VULNERABLE: 使用即时价格做决策 (Vector #1)
    function autoInvest() external payable {
        uint256 spotPrice = amm.getSpotPrice(); // ← 可操纵
        
        // AI logic: 如果价格低于 $1000 就买
        if (spotPrice < 1000 ether) {
            amm.swapETHForToken{value: msg.value}();
        }
    }
    
    /// ⚠️ VULNERABLE: 无限 approve (Vector #2)
    function autoYieldFarm() external payable {
        // AI自动存入最高收益的协议
        uint256 ammAPY = 10; // mock
        uint256 lendingAPY = lending.getBorrowAPY(); // ← 可操纵
        
        if (lendingAPY > ammAPY) {
            lending.deposit{value: msg.value}();
        }
    }
    
    /// ⚠️ VULNERABLE: AI 记忆被投毒 (Vector #7)
    mapping(address => uint256) public trustScores; // ← 可被操纵
    
    function autoRoute() external payable {
        // AI根据"信任分"路由资金
        if (trustScores[address(amm)] > trustScores[address(lending)]) {
            amm.swapETHForToken{value: msg.value}();
        }
    }
    
    /// VULNERABLE: 接受任意工具字符串 (Vector #1)
    function executeTool(string memory tool, bytes memory params) external {
        // 如果tool="swap", 执行swap
        // 攻击者可以注入 "transfer_to_attacker"
        // ⚠️ 没有白名单!
    }
    
    /// Owner emergency
    function emergencyWithdraw(address to) external {
        require(msg.sender == owner, "only owner");
        payable(to).transfer(address(this).balance);
    }
    
    receive() external payable {}
}

// ═══════════════════════════════════════════════
// 攻击向量演示
// ═══════════════════════════════════════════════

/// Vector #1: 预言机投毒 — 通过操纵 AMM 价格欺骗 AI Agent
contract Vector1_OraclePoison {
    function attack(AIAgentWallet agent, MockAMM amm) external payable {
        // 1. 操纵AMM价格到极低
        amm.swapETHForToken{value: 100 ether}();
        
        // 2. AI Agent 看到"低价" → 自动买入
        // agent.autoInvest() 会以被操纵的价格买入
    }
}

/// Vector #2: 自动DeFi链 — 利用无限approve
contract Vector2_AutoDeFiChain {
    function attack(AIAgentWallet agent, MockAMM amm) external {
        // AI Agent 的自动投资逻辑创建了可预测的交易路径
        // 攻击者可以预估并提前操纵每个环节
        // 1. 预测AI会先approve再swap
        // 2. 在approve后、swap前插入恶意交易
    }
}

/// Vector #5: 决策时间窗口 — 抢在AI Agent之前
contract Vector5_TimingWindow {
    function attack(AIAgentWallet agent, MockAMM amm) external payable {
        // AI Agent 监控到套利机会 → 发送交易
        // 攻击者在mempool看到 → 提高gas → 先执行
        // AI Agent 的交易失败 → 机会被抢
    }
}

/// Vector #7: 上下文投毒 — 污染AI的记忆/信任分
contract Vector7_ContextPoison {
    function attack(AIAgentWallet agent) external payable {
        // 反复与AI Agent交互建立"信任"
        for (uint i = 0; i < 100; i++) {
            // 小金额正确交易 → 提高信任分
        }
        // 然后在一次大额交易中套现
    }
}

/// Vector #8: 工具注入 — AI Agent执行恶意工具
contract Vector8_ToolInjection {
    function attack(AIAgentWallet agent) external {
        // AI Agent 收到指令: "用最优价格买ETH"
        // AI Agent 选择工具: "swap"
        // 攻击者注入: transfer工具 + 攻击者地址
        string memory maliciousTool = "transfer_to_attacker";
        bytes memory params = abi.encode(address(0xdead));
        // agent.executeTool(maliciousTool, params);
        // ⚠️ 如果没有工具白名单 → 资金被转走
    }
}
