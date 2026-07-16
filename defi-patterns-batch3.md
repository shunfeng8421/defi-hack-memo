# DeFi 核心漏洞 — 第 3 批 (模式11-15)

## 模式 11: 闪电贷 + 治理攻击组合

### 原理
```
1. 闪电贷借 1 亿治理代币
2. 用这些代币发起投票 → 通过恶意提案
3. 提案执行后 → 还闪电贷
4. 净效果: 一个区块内控制了协议

真实案例: 2021 年 Cream Finance 被黑 ($130M)
```

### 修复
- 投票需要快照（拍摄投票时的余额快照）
- 提案到执行之间有时间锁（至少 48 小时）
- 关键更改需要多签

---

## 模式 12: ERC-20 Approve 竞争 (Frontrunning)

### 原理
```
Alice: approve(Bob, 100)       → 交易池
Bob:   看到待确认的交易
Bob:   transferFrom(Alice, Bob, 100)
Bob:   提交 approve(Alice, Bob, 200) → 抢先确认
结果: Bob 得到了 200 的授权而不是 100

标准修复: approve 前先设置为 0
```

### 检查
- [ ] approve 前是否有 `approve(spender, 0)` 操作？
- [ ] 是否用了 `increaseAllowance` / `decreaseAllowance`？

---

## 模式 13: ERC-721 重入

### 原理
```
ERC-721 的 safeTransferFrom 会调用接收者的 onERC721Received
如果接收者是攻击合约 → 可以在回调中再次调用 transferFrom
→ 重复提取同一 NFT
```

### 修复
- 先更新状态再转账 (checks-effects-interactions)
- 或者用 `transferFrom` (非 safe 版本)

---

## 模式 14: storage 碰撞 (Delegated Call)

### 原理
```
Proxy 合约和 Logic 合约共享同一个 storage 布局
如果:
  Proxy.slot[0] = owner
  Logic.slot[0] = tokenBalance
  
delegatecall(Logic) 会覆盖 Proxy 的 slot[0]
→ 攻击者可以改 owner
```

### 修复
- 确保 Proxy 和 Logic 的 storage 布局一致
- 使用 OpenZeppelin 的 ERC-1967 代理
- 永远不要在逻辑合约的 slot[0] 放关键变量

---

## 模式 15: 自毁合约 + 强制发送 ETH

### 原理
```
合约 A: 假设 address(this).balance 永远不会增加
攻击者: 创建一个合约 → 预存 ETH → SELFDESTRUCT → ETH 强制发给合约 A

后果:
  - 打破了协议的 accounting 假设
  - 某些函数可能因为 "余额看起来多了" 而出错
```

### 修复
- 永远不要依赖 `address(this).balance` 作为关键条件
- 用内部记账变量代替

---

## Slither 可以检测哪些？

| 模式 | Slither 能检测 | 不能检测 |
|------|:--:|------|
| 重入 | ✅ reentrancy-eth | — |
| 未授权访问 | ✅ access-control | — |
| 整数溢出 | ✅ | — |
| storage 碰撞 | ✅ upgradeable-check | — |
| 闪电贷 | ❌ | ✅ 需要理解业务 |
| 价格操纵 | ❌ | ✅ 需要理解业务 |
| 治理攻击 | ❌ | ✅ 需要理解业务 |
| 跨链签名 | ❌ | ✅ 需要理解业务 |
