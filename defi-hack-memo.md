# Blockchain DeFi Hack Memo

> 区块链去中心化金融黑客攻击备忘录
> Compiled by shunfeng8421 — July 15, 2026

## 攻击模式分类 (50 Patterns)

### 1. 闪电贷 + 价格操纵 (Flash Loan + Price Oracle Manipulation)
*最赚钱的攻击类型，占 DeFi 被盗资金的 40% 以上*

| 事件 | 年份 | 损失 | 原理 |
|------|:--:|:--:|------|
| bZx | 2020 | $50M | 闪电贷借 ETH → 操纵 Uniswap 池 → 扭曲价格 → 套利 |
| Harvest Finance | 2020 | $25M | 闪电贷操纵 USDT/USDC Curve 池 → 利用扭曲后的价格 |
| PancakeBunny | 2021 | $45M | 闪电贷借 BNB → 操纵池子 → 铸币大量 BUNNY → 砸盘 |
| Beluga | 2023 | $~2M | 闪电贷操纵 Curve 池 → 利用借贷协议中的瞬时价格 |
| Makina | 2026 | $5.1M | 闪电贷操纵 DUSD/USDC 池 → 多步套利 |

**检测**: `getReserves()` → ❌ | `oracle.consult()` → ✅ | `TWAP` → ✅

---

### 2. 重入攻击 (Reentrancy)

| 事件 | 年份 | 损失 | 原理 |
|------|:--:|:--:|------|
| The DAO | 2016 | $60M | split 函数 → fallback 递归 → 重复提取 ETH |
| LendfMe | 2020 | $25M | ERC-777 tokensToSend 回调 → withdraw 未锁定 → 重复提现 |
| Cream | 2021 | $130M | ERC-777 + Uniswap V2 回调组合 |
| BurgerSwap | 2021 | $7M | 闪电贷 + Uniswap V2 回调 → 多步重入 |

**修复**: `checks-effects-interactions` | `ReentrancyGuard` | 先更新余额后转账

---

### 3. 整数溢出/精度损失

| 事件 | 年份 | 损失 | 原理 |
|------|:--:|:--:|------|
| BEC (Beauty Chain) | 2018 | $1.5B* | batchTransfer 中 _value * 2 溢出 → 无限铸币 |
| SmartMesh (SMT) | 2018 | $140M | 转账精度截断 → 余额不匹配 → 合约余额被掏空 |
| Uranium | 2021 | $50M | 除法截断 → swap 计算错误 → 被套利 |

**检测**: `pragma solidity <0.8.0` → ⚠️ 需要 SafeMath | 除法计算 → 先乘后除检查

---

### 4. 闪贷 + 治理攻击

| 事件 | 年份 | 损失 | 原理 |
|------|:--:|:--:|------|
| Cream | 2021 | $130M | 闪贷 AMP → 投票权 → 恶意提案 → 提取全部资金 |
| TrueFi | 2022 | $4M | 闪贷 TRU → 投票 → 修改参数 |
| Sushi | 2023 | $3M | 闪贷 xSUSHI → 投票 → 路由资金 |

**修复**: 快照投票 | 时间锁 | 多签

---

### 5. 跨链桥漏洞

| 事件 | 年份 | 损失 | 原理 |
|:----:|:--:|:--:|------|
| Wormhole | 2022 | $320M | 签名验证漏洞 → 伪造 VA 签署提现 |
| Nomad | 2022 | $152M | 消息验证被绕过 → 任何人都可提现 |
| PolyNetwork | 2021 | $610M | 跨链消息验证函数存在逻辑漏洞 |
| Orbit Chain | 2024 | $81M | 多签验证器被控制 |

**检测**: `chainID` 检查 | `nonce` 去重 | 验证器配额

---

### 6. AMM 池操纵

| 事件 | 年份 | 损失 | 原理 |
|:----:|:--:|:--:|------|
| Balancer | 2020 | $500K | ERC-777 回调 → 重复提取 LP |
| Uranium | 2021 | $50M | swap 公式计算错误 → 任意价格 |
| Platypus | 2023 | $2M | 单边添加流动性 → 操纵池子 |

---

### 7. 借贷清算操纵

| 事件 | 年份 | 损失 | 原理 |
|:----:|:--:|:--:|------|
| Euler | 2023 | $197M | 闪贷 → 操纵预言机 → 跳过清算 → 坏账 |
| Rari Capital | 2021 | $10M | 价格预言机操控 → 借出超过抵押品 |
| Cream | 2021 | $130M | 闪贷 AMP → 利用价格差异 |

---

### 8. 代理/升级漏洞

| 事件 | 年份 | 损失 | 原理 |
|:----:|:--:|:--:|------|
| Parity 多签 | 2017 | $153K ETH | 库合约自毁 → 锁定全部资金 |
| Parity 钱包 | 2017 | $280M | initWallet 可被任意调用 → 夺取所有权 |
| Audius | 2022 | $1M | 代理存储碰撞 → 修改所有者 |

**检测**: `delegatecall` | `UUPS` | storage gap | `_disableInitializers`

---

### 9. 闪电贷 + 重入组合

| 事件 | 年份 | 损失 | 原理 |
|:----:|:--:|:--:|------|
| BurgerSwap | 2021 | $7M | 闪电贷 + Uniswap V2 callback + 重入 |
| ValueDeFi | 2021 | $10M | 多步攻击链 |
| Uranium | 2021 | $50M | 精度 + 重入组合 |

---

### 10. 授权/权限漏洞

| 事件 | 年份 | 损失 | 原理 |
|:----:|:--:|:--:|------|
| PolyNetwork | 2021 | $610M | keeper 角色可调用敏感函数 |
| TransitSwap | 2022 | $250K | approve 参数可被控制 → 授权转出 |
| BSC 跨链桥 | 2022 | $570M | 伪造验证消息 → 绕过验证器签名 |

---

## 按年份统计

```
2017: 2 事件 — Parity 多签/钱包 (EVM 早期)
2018: 3 事件 — BEC/SmartMesh/SpankChain (代币泡沫)
2020: 8 事件 — DeFi Summer 开端
2021: 35 事件 — DeFi 爆发年 (Cream/PolyNetwork/Bunny)
2022: 128 事件 — 跨链/桥攻击高峰期 (Wormhole/Nomad)
2023: 213 事件 — 攻击工业化
2024: 187 事件 — L2/多链攻击增加
2025: 159 事件 — AI 代币攻击出现
2026: 88 事件 — (截至 7 月)
```

**总计: 824+ 事件, 预计总损失 > $10B**

---

## 十大损失事件

| # | 事件 | 年份 | 损失 | 模式 |
|:--:|------|:--:|:--:|:--:|
| 1 | PolyNetwork | 2021 | $610M | 跨链 + 权限 |
| 2 | BSC 跨链桥 | 2022 | $570M | 签名伪造 |
| 3 | Wormhole | 2022 | $320M | 签名验证 |
| 4 | Parity 钱包 | 2017 | $280M | 权限漏洞 |
| 5 | Euler | 2023 | $197M | 闪贷+清算 |
| 6 | Cream | 2021 | $130M | 闪贷+治理+重入 |
| 7 | Nomad | 2022 | $152M | 跨链消息 |
| 8 | SmartMesh | 2018 | $140M | 整数溢出 |
| 9 | Beefy | 2025 | $1.5B | Bybit 相关 |
| 10 | Truebit | 2026 | $8.5K ETH | 精度漏洞 |

---

## 50 模式映射

| 模式 | 对应真实事件 | 检测方法 |
|:----:|------|------|
| 1. 闪贷+价格操纵 | bZx, Harvest, PancakeBunny | `getReserves()` → TWAP |
| 2. 重入 | The DAO, LendfMe, Cream | checks-effects-interactions |
| 3. TWAP 不足 | 多个 DEX 攻击 | `period < 1800` |
| 4. 滑点 | 三明治攻击 | `minAmountOut` 缺失 |
| 5. ERC-4626 | 通胀攻击 | 首次存款 offset |
| 6. 清算操纵 | Euler, Rari | 价格来源检查 |
| 7. AMM 精度 | Uranium, BEC | 除法截断检查 |
| 8. 治理攻击 | Cream, TrueFi | 快照+时间锁 |
| 9. 利率操纵 | 多个借贷协议 | 更新顺序检查 |
| 10. 跨链签名 | Wormhole, PolyNetwork | chainID+nonce+多签 |
| ... | ... | ... |
| 50. Storage碰撞 | Audius, Parity | EIP-1967 slots |

---

## 修复优先级

| 优先级 | 模式 | 平均损失 |
|:------:|:----:|:--------:|
| 🔴 P0 | 闪贷+价格操纵 | $50M+ |
| 🔴 P0 | 跨链签名绕过 | $200M+ |
| 🔴 P0 | 重入 | $50M+ |
| 🟡 P1 | 治理攻击 | $10M+ |
| 🟡 P1 | 权限漏洞 | $10M+ |
| 🔵 P2 | 整数溢出 | $100M+ (但少发) |
| 🔵 P2 | 精度损失 | $10M |
