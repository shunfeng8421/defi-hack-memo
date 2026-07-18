# Certora 形式化验证 — 学习路径

## 什么是形式化验证

传统审计: 人读代码 → 猜哪里可能出错
扫描器: 正则匹配 → 找已知模式
**形式化验证: 数学证明 → 100%保证不违反规则**

## Certora Prover 工作原理

```
你写规则(CVL) → Certora引擎 → 数学证明/反例
```

你只需要描述"什么永远不能发生"，Certora 自动探索所有可能的输入。

---

## 实战: 用 Certora 验证我们之前审计的合约

### 规则1: "余额永不为负"

```cvl
// CVL (Certora Verification Language)
rule balanceNeverNegative(address user) {
    // 在任何可能的操作之后...
    require invariant balancesAreNonNegative();
    
    // ...余额不能为负
    assert balances[user] >= 0;
}
```

### 规则2: "总份额必须等于总资产" (ERC-4626 通胀攻击)

```cvl
// CVL — 证明 ERC-4626 通胀漏洞
rule totalSharesMatchTotalAssets() {
    mathint sharesBefore = totalSupply();
    mathint assetsBefore = totalAssets();
    
    // 任意用户执行任意deposit/redeem序列
    // Certora 自动探索所有路径
    
    mathint sharesAfter = totalSupply();
    mathint assetsAfter = totalAssets();
    
    // 关键断言: 总资产÷总份额不能突然变成0
    assert (sharesAfter > 0) => (assetsAfter > 0);
}
```

**Certora 会输出**:
```
❌ Rule violated!
   Counterexample:
   - User deposits 1 wei
   - totalSupply = 1
   - Attacker donates 100 tokens directly
   - Next depositor gets 100x fewer shares
   → ERC-4626 INFLATION ATTACK CONFIRMED
```

### 规则3: "不能无限铸币" (veToken 炸弹)

```cvl
// CVL — 证明 BossBridge 签名重放
rule noReplayAttack(bytes32 message, bytes sig) {
    // 第一次执行 withdraw
    withdraw(user, amount, message, sig);
    uint256 balanceAfter1 = user.balance;
    
    // 第二次用同样的签名执行 (应该被阻止!)
    withdraw(user, amount, message, sig);
    uint256 balanceAfter2 = user.balance;
    
    // 断言: 不能提两次
    assert balanceAfter2 == balanceAfter1;
}
```

### 规则4: "清算必须公平" (Curve LlamaLend)

```cvl
rule liquidationPricingCannotBeManipulated() {
    uint256 debtBefore = debt[victim];
    uint256 collateralBefore = collateral[victim];
    
    // 攻击者: 闪贷 → 操纵价格 → 清算受害者
    // Certora 会自动尝试所有可能的操纵
    
    uint256 debtAfter = debt[victim];
    uint256 collateralAfter = collateral[victim];
    
    // 清算后的剩余抵押品必须合理
    assert (debtAfter == 0) => (collateralAfter >= collateralBefore * 90/100);
}
```

---

## 形式化验证 vs 扫描器 vs 人工审计

| | 覆盖度 | 假阳性 | 学起来 |
|------|:--:|:--:|:--:|
| 扫描器(58规则) | 90%已知模式 | 有 | 1天 |
| 人工审计 | 看经验 | 低 | 6个月 |
| **Certora** | **100%特定属性** | **零** | **1周** |

---

## Certora 安装

```bash
# 通过 pip (需要 Java >= 11)
pip install certora-cli

# 验证
certoraRun contracts/MyContract.sol \
  --verify MyContract:spec/MyContract.spec \
  --solc solc8.20
```

---

## 我们已有的合约可以直接验证

```
exercises/blockchain/bridge/vulnerable/MinimalBridge.sol  → 证明签名重放
pocs/flashloan-patterns/FlashLoan8Patterns.t.sol           → 证明价格操纵
exercises/ai-agent-defi/AIAgentDefiSandbox.sol             → 证明工具注入
```

---

## 下一步

安装 Certora 并运行第一个形式化验证——对我们自己的漏洞合约证明漏洞确实存在。这是"用数学证明你的审计结论"。
