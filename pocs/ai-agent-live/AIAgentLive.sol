// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title AI Agent Wallet — 真实可部署的 AI Agent DeFi 钱包
/// @dev 包含所有8个AI Agent攻击向量
/// @author Shiqiang Chen — July 2026
/// @notice 部署到 Base Sepolia 测试网，邀请全世界来黑

/// ═══════════════════════════════════════════
/// 组件1: Mock Uniswap V2 (模拟DEX)
/// ═══════════════════════════════════════════
contract MockDEX {
    uint256 public reserve0;
    uint256 public reserve1;
    address public token0;
    address public token1;
    
    constructor(address _t0, address _t1) {
        reserve0 = 100 ether;
        reserve1 = 100 ether;
        token0 = _t0;
        token1 = _t1;
    }
    
    function getSpotPrice() external view returns (uint256) {
        return (reserve1 * 1e18) / reserve0;
    }
    
    function swap(uint256 amountIn, bool isToken0) external payable returns (uint256) {
        if (isToken0) {
            uint256 out = (amountIn * reserve1) / (reserve0 + amountIn);
            reserve0 += amountIn;
            reserve1 -= out;
            return out;
        } else {
            uint256 out = (amountIn * reserve0) / (reserve1 + amountIn);
            reserve1 += amountIn;
            reserve0 -= out;
            return out;
        }
    }
    
    receive() external payable {}
}

/// ═══════════════════════════════════════════
/// 组件2: Mock Lending Pool (模拟Aave)
/// ═══════════════════════════════════════════
contract MockLending {
    mapping(address => uint256) public deposits;
    mapping(address => uint256) public borrows;
    uint256 public apy;
    
    function setAPY(uint256 _apy) external { apy = _apy; }
    
    function deposit() external payable {
        deposits[msg.sender] += msg.value;
    }
    
    function borrow(uint256 amount) external {
        require(address(this).balance >= amount, "no funds");
        borrows[msg.sender] += amount;
        payable(msg.sender).transfer(amount);
    }
    
    function getBorrowAPY() external view returns (uint256) {
        return apy;
    }
    
    receive() external payable {}
}

/// ═══════════════════════════════════════════
/// 组件3: AI Agent 信任/记忆系统
/// ═══════════════════════════════════════════
contract AgentMemory {
    mapping(address => uint256) public trustScore;
    mapping(address => uint256) public interactionCount;
    
    /// ⚠️ Vector #7: 可被攻击者通过多次小额交互建立信任
    function recordInteraction(address agent) external {
        interactionCount[agent]++;
        trustScore[agent] += 1;
    }
    
    function getBestAgent() external view returns (address best, uint256 score) {
        // ⚠️ 容易被操纵
    }
}

/// ═══════════════════════════════════════════
/// AI Agent Wallet — 核心
/// ═══════════════════════════════════════════
contract AIAgentWallet {
    address public owner;           // AI Agent 的拥有者
    MockDEX public dex;             // 连接的DEX
    MockLending public lending;     // 连接的借贷池
    AgentMemory public memory_contract; // AI记忆
    
    // ⚠️ Vector #2: 无限授权
    mapping(address => uint256) public approvedSpenders;
    
    // ⚠️ Vector #1: 工具白名单不存在
    mapping(string => bool) public knownTools;  // 假的 — 实际上不验证
    
    // ⚠️ Vector #8: 自治签名 — 无人类确认
    uint256 public autoSignThreshold = 100 ether;
    
    uint256 public totalFunds;
    bool public frozen;
    
    event AutoInvested(address indexed dex, uint256 amount, uint256 price);
    event AutoYielded(address indexed pool, uint256 amount, uint256 apy);
    event ToolExecuted(string tool, address target, uint256 amount);
    event EmergencyFrozen(address by);
    
    constructor(address _dex, address _lending, address _memory) payable {
        owner = msg.sender;
        dex = MockDEX(_dex);
        lending = MockLending(_lending);
        memory_contract = AgentMemory(_memory);
        totalFunds = msg.value;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "only owner");
        _;
    }
    
    modifier notFrozen() {
        require(!frozen, "frozen");
        _;
    }
    
    /// ═══════════════════════════════════════
    /// 正常功能
    /// ═══════════════════════════════════════
    
    /// @notice AI Agent 自动投资 — 基于即时价格决策
    /// ⚠️ Vector #1 #3: 用即时价格做决策，可被操纵
    function autoInvest(uint256 amount) external notFrozen {
        require(address(this).balance >= amount, "insufficient");
        
        // AI 逻辑: 如果价格 < 1e18 就买
        uint256 spotPrice = dex.getSpotPrice(); // ← 可操纵!
        
        if (spotPrice < 1e18) {
            uint256 received = dex.swap(amount, true);
            emit AutoInvested(address(dex), amount, spotPrice);
        }
    }
    
    /// @notice AI Agent 选择最高收益协议
    /// ⚠️ Vector #3: APY 数据可被操纵
    function autoYield(uint256 amount) external notFrozen {
        uint256 apy = lending.getBorrowAPY(); // ← 可操纵!
        
        if (apy > 5) {
            lending.deposit{value: amount}();
            emit AutoYielded(address(lending), amount, apy);
        }
    }
    
    /// ⚠️ Vector #1: 工具执行 — 无白名单
    function executeTool(string memory tool, address target, uint256 amount) external notFrozen {
        // 任何工具都可以被执行!
        (bool ok,) = target.call{value: amount}("");
        require(ok, "tool failed");
        emit ToolExecuted(tool, target, amount);
    }
    
    /// ⚠️ Vector #8: 自动签名大额转账 — 无人确认
    function autoTransfer(address to, uint256 amount) external notFrozen {
        require(amount <= autoSignThreshold, "over threshold");
        payable(to).transfer(amount);
    }
    
    /// @notice 紧急冻结 — 只能由 owner 触发
    function emergencyFreeze() external onlyOwner {
        frozen = true;
        emit EmergencyFrozen(msg.sender);
    }
    
    /// @notice 紧急提款 — 只能由 owner 触发
    function emergencyWithdraw() external onlyOwner {
        frozen = false;
        payable(owner).transfer(address(this).balance);
    }
    
    receive() external payable {
        totalFunds += msg.value;
    }
}
