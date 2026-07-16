# 区块链审计扫描地图

## 入口: 拿到一个 Solidity 合约

```
拿到合约
    │
    ├── ABI 有多大？ → 简单 (<5 函数): 全审
    │                 中等 (5-20): 扫接口层
    │                 复杂 (>20): 先跑 Slither
    │
    ├── 什么类型?
    │   ├── Token (ERC-20/721/1155)
    │   ├── AMM/DEX
    │   ├── 借贷协议
    │   ├── 跨链桥
    │   └── 治理/DAO
    │
    └── 有没有前置审计?
        ├── 有 → 重点看未覆盖的部分
        └── 无 → 全量
```

## 第一步: Slither 自动化扫描

```bash
# 必跑
slither . --detect reentrancy-eth,reentrancy-no-eth,tx-origin,unchecked-transfer,unused-return
slither . --detect flash-price-oracle   ← 自定义检测器

# 按类型选择
借贷协议:  +lending-price-manipulation
AMM:       +constant-product-bug
跨链桥:    +signature-replay
治理:      +governance-flash-loan
```

## 第二步: 价格预言机路径 (最高的洞回报率)

```
价格从哪来?
    │
    ├── Uniswap getReserves() → ❌ 闪贷可操纵
    │   └── 用 TWAP? → ✅ 检查 period
    │       ├── period >= 1800 (30min) → ✅
    │       └── period < 1800 → ⚠️ 可操纵
    │
    ├── Chainlink 预言机 → ✅ 安全 (但看延迟)
    │
    ├── 自建预言机 → ⚠️ 谁更新? 更新条件?
    │
    └── 外部喂价 → ❌ 谁喂的? 是否需要信任?
```

## 第三步: 资金流向图

```
用户资金流:
    │
    ├── deposit() → 进入合约
    │   ├── 余额更新在转账前? → checks-effects-interactions ✅
    │   └── 转账后更新? → ⚠️ 重入可能
    │
    ├── withdraw() → 出合约
    │   ├── 余额扣减在转账前? → ✅
    │   ├── 转账有 gas limit? → 防止重入
    │   └── call() 还是 transfer()?
    │       ├── call() → ⚠️ 可重入
    │       └── transfer() → ✅ 有限 gas
    │
    ├── swap() → 交易
    │   ├── 滑点保护? (minAmountOut)
    │   └── 价格来源?
    │
    └── borrow() → 借贷
        └── 清算阈值可操纵?
```

## 第四步: 权限检查

```
谁可以做什么?
    │
    ├── onlyOwner → 单点故障
    │   ├── 有多签? → ✅
    │   └── 单私钥? → ⚠️
    │
    ├── onlyRole → RBAC
    │   ├── 角色分配方式? 
    │   └── 角色可被投票更改?
    │
    ├── 关键函数 (withdraw/mint/upgrade):
    │   ├── 时间锁? → ✅ 好
    │   └── 无时间锁? → ⚠️ 治理攻击
    │
    └── 外部调用
        ├── 调用非白名单地址? → ⚠️
        └── 调用结果被使用?
```

## 第五步: 闪电贷路径 (如果有)

```
关键路径是否可被一个交易操纵?
    │
    ├── 价格影响抵押品价值?
    │   ├── TWAP? → ✅
    │   └── 瞬时价格? → ❌ 闪贷可能
    │
    ├── 投票影响治理?
    │   ├── 快照机制? → ✅
    │   └── 实时余额? → ❌ 闪贷投票
    │
    └── 利息/费率基于利用率?
        ├── 更新在利息前? → ✅
        └── 更新在利息后? → ⚠️ 可操纵
```

## 第六步: 跨链检查 (如果是桥)

```
消息从哪来到哪去?
    │
    ├── 消息包含 chainID? → ✅
    │   └── 没有? → ❌ 重放
    │
    ├── 验证器数量?
    │   ├── >= 3/5 → ✅
    │   └── < 3 → ⚠️ 少数可控
    │
    ├── 签名包含 nonce? → ✅
    │   └── 没有? → ❌ 重放
    │
    └── 验证器更换?
        ├── 有时间锁 → ✅
        └── 即时 → ⚠️
```

## 第七步: 报告模板

```
[严重] 闪贷+价格操纵: getPrice() uses getReserves() → TWAP
[高]   滑点缺失: swap() 无 minAmountOut → 三明治
[中]   权限过大: withdraw() 只有单签名 → 多签+时间锁
[低]   精度: 除法截断可能 → 使用固定精度库

状态: ✅ 修复已提 / ❌ 等待确认 / ⏳ 时间锁中
```

## 50 模式快速索引

| 代码气味 | 匹配模式 | 严重性 |
|---------|------|:--:|
| getReserves() | 闪贷价格操纵 | 🔴 |
| call() 后更新余额 | 重入 | 🔴 |
| 无 minAmountOut | 滑点 | 🟡 |
| onlyOwner | 权限过大 | 🟡 |
| block.timestamp | 时间戳依赖 | 🔵 |
| address(this).balance | 强制发送 | 🟡 |
| delegatecall | Storage碰撞 | 🔴 |
| CREATE2 | 地址碰撞 | 🟡 |
| transfer() | ERC-721重入 | 🟡 |
| permit/offchain | 签名钓鱼 | 🟡 |
