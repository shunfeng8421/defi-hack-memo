# DeFi 核心漏洞 — 第 2 批实战

## 模式 6: 借贷清算操纵

### 原理

```
正常清算:
  用户抵押 100 ETH (值 $300,000)
  借出 200,000 USDC (LTV = 66%)
  价格跌到 $266,000 → LTV 超 75% → 可清算

攻击:
  攻击者闪电贷拉高 ETH 价格 → LTV 看似安全
  用户无法被清算 → 保护了坏账 → 协议损失
```

### 检查清单

- [ ] 清算使用链上价格还是 TWAP？
- [ ] 是否允许外部预言机？
- [ ] 健康因子计算是否可被操纵？

---

## 模式 7: AMM 恒定乘积公式攻击

### 公式回顾

```
x * y = k
token0 储备 * token1 储备 = 恒定乘积
swap(tokenIn) → token0 增加 → token1 按比例减少
```

### 漏洞: 精度损失

```solidity
// ❌ VULNERABLE: 除法精度丢失
function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) pure returns (uint) {
    return amountIn * reserveOut / (reserveIn + amountIn);  
    // 如果 amountIn 很小 → 结果为 0 → 可以0成本swap
}
```

### 修复

```solidity
// ✅ FIXED: 先乘后除 + 最小1
function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) pure returns (uint) {
    uint amountInWithFee = amountIn * 997;  // 0.3% 手续费
    uint numerator = amountInWithFee * reserveOut;
    uint denominator = reserveIn * 1000 + amountInWithFee;
    return numerator / denominator;  // 标准 Uniswap V2 公式
}
```

---

## 模式 8: 治理攻击

### 原理

```
攻击者获得治理权后可以:
1. 改预言机地址 → 换成自己控制的
2. 改费用参数 → 提取全部资金
3. 升级合约 → 植入后门
4. 铸造代币 → 通胀攻击
```

### 常见漏洞模式

```solidity
// ❌ VULNERABLE: 提案执行无时间锁
function executeProposal(address target, bytes calldata data) external onlyGovernance {
    (bool ok, ) = target.call(data);  // 立即执行, 用户来不及退出
    require(ok);
}

// ✅ FIXED: 时间锁
function executeProposal(address target, bytes calldata data) external onlyGovernance {
    require(block.timestamp >= queuedAt + TIMELOCK_DELAY, "时间锁未到");
    (bool ok, ) = target.call(data);
    require(ok);
}
```

### 检查清单

- [ ] 治理投票权是否可借贷攻击？(Flash loan → 借票 → 投票 → 还票)
- [ ] 提案是否有时间锁？
- [ ] 是否有多签保护？
- [ ] 治理能否修改关键参数？（预言机/费用/升级）

---

## 模式 9: 借贷利率操纵

### 原理

```
借贷协议的资金利用率 = 已借出 / 总存入
利率 = 根据利用率动态调整

攻击:
1. 攻击者存入大量资金 → 利用率降低 → 利率降低
2. 用极低利率借出资金
3. 或: 借出 → 利用率提高 → 利率提高 → 做空利率
```

### 检查

- [ ] 利率模型是否考虑"一个账户的大额操作"？
- [ ] 利率更新是否在利息累积之前？

---

## 模式 10: 跨链桥的验证器签名

### 原理

```
跨链桥:
  Ethereum: 用户存入 100 ETH
  验证器: 签名"已收到100 ETH"
  Solana: 铸币 100 WETH

漏洞:
  验证器私钥泄露 → 伪造提现请求
  验证器阈值不足 → 少数验证器可以签过
  重放攻击 → 同一个签名在多个链提现
```

### 检查清单

- [ ] 签名验证是否包括 chainID？（防止重放）
- [ ] 验证器数量是否足够？（> 3/5 或 5/9）
- [ ] 验证器更换是否有时间锁？
- [ ] 消息中是否包含 random nonce？

---

## 综合练习

### 练习 1

```solidity
contract GovernanceToken {
    mapping(address => uint) public balance;
    mapping(address => mapping(address => uint)) public allowance;
    
    function delegate(address to) external {
        // 委托投票权
    }
    
    function transferFrom(address from, address to, uint amount) external returns (bool) {
        // 标准 ERC-20 transferFrom
    }
}
```

**问题：** 攻击者用闪电贷借了 1 亿个治理代币 → 投票 → 通过恶意提案 → 还代币。需要什么修复？

### 练习 2

```solidity
contract Bridge {
    mapping(bytes32 => bool) usedSignatures;
    address[] validators;
    uint constant THRESHOLD = 3;
    
    function execute(bytes calldata msg, bytes[] calldata sigs) external {
        // 验证签名足够
        require(sigs.length >= THRESHOLD, "签名不够");
        // 验证每个签名的有效性
        for (uint i = 0; i < sigs.length; i++) {
            address signer = recoverSigner(msg, sigs[i]);
            require(isValidator[signer], "无效签名者");
        }
        // 执行跨链消息
    }
}
```

**问题：** 有什么漏了？怎么修复？
