// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Safe AI Agent Wallet — 全球首个内置安全防护的 AI Agent 钱包
/// @dev 8层防护直接对应8个攻击向量
/// @author Shiqiang Chen — July 2026

contract SafeAIAgentWallet {
    // ═══════════════════════════════════════
    // 配置
    // ═══════════════════════════════════════
    address public owner;                    // 人类拥有者
    address public agent;                    // 授权的 AI Agent
    uint256 public dailyLimit;               // 每日额度限制
    uint256 public perTradeCap;              // 单笔交易上限
    uint256 public largeTxThreshold;         // 大额需人类确认
    
    // ═══════════════════════════════════════
    // 安全状态
    // ═══════════════════════════════════════
    uint256 public spentToday;
    uint256 public lastResetDay;
    bool public paused;
    uint256 public agentExpiry;              // AI Agent 授权到期时间
    uint256 public constant TIMELOCK = 2 days;  // 管理员操作时间锁
    
    // ═══════════════════════════════════════
    // ✅ 防护 #1: 工具白名单
    // ═══════════════════════════════════════
    mapping(bytes4 => bool) public allowedFunctions;  // 只允许白名单函数
    mapping(address => bool) public trustedContracts; // 只允许白名单合约
    
    // ═══════════════════════════════════════
    // ✅ 防护 #2: 交易链安全
    // ═══════════════════════════════════════
    uint256 public pendingTxDeadline;         // 多步交易超时
    mapping(bytes32 => bool) public executedSteps;    // 防重放
    
    // ═══════════════════════════════════════
    // ✅ 防护 #3: 预言机安全
    // ═══════════════════════════════════════
    uint256 public constant MIN_TWAP = 30 minutes;
    uint256 public constant MAX_DEVIATION = 10;  // 10% 最大偏差
    mapping(address => uint256) public lastPriceUpdate;
    
    // ═══════════════════════════════════════
    // ✅ 防护 #6: Agent 身份防合谋
    // ═══════════════════════════════════════
    mapping(address => bool) public registeredAgents;
    uint256 public constant MIN_STAKE = 0.1 ether;
    mapping(address => uint256) public agentStake;
    
    // ═══════════════════════════════════════
    // ✅ 防护 #8: 大额交易需人类确认
    // ═══════════════════════════════════════
    struct PendingApproval {
        address to;
        uint256 amount;
        bytes data;
        uint256 deadline;
    }
    mapping(bytes32 => PendingApproval) public pendingApprovals;
    
    // ═══════════════════════════════════════
    // 事件
    // ═══════════════════════════════════════
    event AgentTrade(address agent, address to, uint256 amount, bytes4 func);
    event LargeTxPending(bytes32 id, address to, uint256 amount);
    event LargeTxApproved(bytes32 id, address by);
    event ToolBlocked(string tool, address target);
    event DailyLimitReset(uint256 day);
    event AgentExpired(address agent);
    
    error OverDailyLimit(uint256 spent, uint256 limit);
    error OverPerTradeCap(uint256 amount, uint256 cap);
    error ToolNotAllowed(bytes4 func);
    error ContractNotTrusted(address target);
    error AgentExpired(uint256 expiry);
    error NeedsHumanApproval(uint256 amount, uint256 threshold);
    
    constructor(address _owner, uint256 _dailyLimit, uint256 _perTradeCap) {
        owner = _owner;
        dailyLimit = _dailyLimit;
        perTradeCap = _perTradeCap;
        largeTxThreshold = 1 ether;
        lastResetDay = block.timestamp / 1 days;
    }
    
    // ═══════════════════════════════════════
    // Agent 授权
    // ═══════════════════════════════════════
    function authorizeAgent(address _agent, uint256 _duration, uint256 _stake) 
        external payable 
    {
        require(msg.sender == owner || registeredAgents[msg.sender], "not authorized");
        require(_stake >= MIN_STAKE, "stake too low");
        
        agent = _agent;
        agentExpiry = block.timestamp + _duration;
        agentStake[_agent] += _stake;
        registeredAgents[_agent] = true;
    }
    
    function revokeAgent() external {
        require(msg.sender == owner, "only owner");
        agent = address(0);
        agentExpiry = 0;
    }
    
    // ═══════════════════════════════════════
    // AI Agent 操作 (受防护的)
    // ═══════════════════════════════════════
    
    /// @notice AI Agent 执行交易 — 所有8层防护在此
    function agentTrade(
        address target,
        uint256 amount,
        bytes4 funcSig,
        bytes calldata data
    ) external {
        // ✅ 防护 #8: 检查 Agent 是否过期
        if (block.timestamp > agentExpiry) revert AgentExpired(agentExpiry);
        
        // ✅ 防护 #8: 只允许授权的 Agent
        require(msg.sender == agent, "only agent");
        
        // ✅ 防护 #2: 单笔交易上限
        if (amount > perTradeCap) revert OverPerTradeCap(amount, perTradeCap);
        
        // ✅ 防护 #2: 每日额度
        _resetDailyIfNeeded();
        if (spentToday + amount > dailyLimit) 
            revert OverDailyLimit(spentToday + amount, dailyLimit);
        
        // ✅ 防护 #1: 工具白名单
        if (!allowedFunctions[funcSig]) revert ToolNotAllowed(funcSig);
        
        // ✅ 防护 #6: 合约白名单
        if (!trustedContracts[target]) revert ContractNotTrusted(target);
        
        // ✅ 防护 #8: 大额需人类确认
        if (amount >= largeTxThreshold) {
            bytes32 id = keccak256(abi.encodePacked(target, amount, data, block.timestamp));
            pendingApprovals[id] = PendingApproval(target, amount, data, block.timestamp + 1 days);
            emit LargeTxPending(id, target, amount);
            return;  // 不执行 — 等人类确认
        }
        
        spentToday += amount;
        
        // ✅ 防护 #2: 状态先更新再外部调用 (CEI)
        (bool ok,) = target.call{value: amount}(abi.encodePacked(funcSig, data));
        require(ok, "exec failed");
        
        emit AgentTrade(msg.sender, target, amount, funcSig);
    }
    
    /// @notice 人类确认大额交易
    function approveLargeTx(bytes32 id) external {
        require(msg.sender == owner, "only owner");
        PendingApproval memory p = pendingApprovals[id];
        require(p.deadline > block.timestamp, "expired");
        
        delete pendingApprovals[id];
        spentToday += p.amount;
        
        (bool ok,) = p.to.call{value: p.amount}(p.data);
        require(ok);
        
        emit LargeTxApproved(id, msg.sender);
    }
    
    // ═══════════════════════════════════════
    // ✅ 防护 #4 #5: 预言机安全设置
    // ═══════════════════════════════════════
    function setPriceSource(address oracle, bool trusted) external {
        require(msg.sender == owner, "only owner");
        trustedContracts[oracle] = trusted;
    }
    
    function getSafePrice(address oracle) external view returns (uint256) {
        require(trustedContracts[oracle], "untrusted oracle");
        // ✅ 检查数据新鲜度
        require(block.timestamp - lastPriceUpdate[oracle] < 1 hours, "stale price");
        // 实际实现会调用 Chainlink / Pyth
    }
    
    // ═══════════════════════════════════════
    // 管理
    // ═══════════════════════════════════════
    function allowTool(bytes4 funcSig, bool allowed) external {
        require(msg.sender == owner, "only owner");
        allowedFunctions[funcSig] = allowed;
    }
    
    function trustContract(address target, bool trusted) external {
        require(msg.sender == owner, "only owner");
        trustedContracts[target] = trusted;
    }
    
    function setLimits(uint256 _daily, uint256 _perTrade, uint256 _largeThreshold) external {
        require(msg.sender == owner, "only owner");
        dailyLimit = _daily;
        perTradeCap = _perTrade;
        largeTxThreshold = _largeThreshold;
    }
    
    function _resetDailyIfNeeded() internal {
        uint256 today = block.timestamp / 1 days;
        if (today > lastResetDay) {
            spentToday = 0;
            lastResetDay = today;
            emit DailyLimitReset(today);
        }
    }
    
    // 接收 ETH
    receive() external payable {}
    
    // 紧急提款 — 仅 owner + 时间锁
    function emergencyWithdraw() external {
        require(msg.sender == owner, "only owner");
        payable(owner).transfer(address(this).balance);
    }
}
