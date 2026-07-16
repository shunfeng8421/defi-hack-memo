# DeFi 核心漏洞 — 第 5 批 (模式43-50)

## 模式 43: Permit 签名钓鱼

```
ERC-20 Permit 允许用户离线签名授权
攻击者构造一个"看起来正常"的 Permit 签名请求
用户签了 → 攻击者拿到授权 → 转走用户的代币

常见钓鱼方式:
  1. 伪装成领取空投 → 让用户签 Permit
  2. 伪装成白名单注册 → 让用户签 Permit
  3. 直接读取链上已有的签名（如果 nonce 被复用）
```

**修复**: 签名消息中包含 `deadline` + 用户可取消授权
**检查**: permit() 是否有 `deadline` 检查？

---

## 模式 44: 再平衡攻击

```
AMM 池在权重调整时需要更新价格
攻击者:
1. 在调整前买入 token A
2. 权重调整导致价格变化
3. 卖出 token A → 无风险套利

如果再平衡过程没有足够的滑点保护 → 可提取大量价值
```

**修复**: 用 TWAP 做再平衡价格 + 限制单次调整比例

---

## 模式 45: 利率模型操纵

```
借贷协议:
借出 → 利用率 ↑ → 利息 ↑
存入 → 利用率 ↓ → 利息 ↓

攻击者:
1. 存入大量资金 → 利用率 ↓ → 利息暴降
2. 以极低利息借出
3. 提取存款 → 利率恢复
4. 利息差被套利
```

**修复**: 利率更新在利息累积之前 + 防止单账户操纵利用率

---

## 模式 46: 费率精度损失

```
计算: 每次收取 0.3% 手续费
A 转给 B 100 → 应扣 0.3 → 精度不足 → 实际扣 0
→ 100 次转账 = 省了 30 手续费 → 套利

Solidity 没有浮点数:
100 * 0.3 / 100 = 0（精度丢失）
100 * 3 / 1000 = 0（同样）
```

**修复**: 使用固定精度乘法（如 WadRayMath）+ 累积费用
**检查**: 费用计算是否在精度允许范围内？

---

## 模式 47: CREATE2 地址碰撞

```
CREATE2 = 可以预计算合约地址
攻击者提前计算将要部署的合约地址
在该地址上预部署一个"看似安全但实际有后门"的合约
等待项目方部署到同一地址 → 取代了项目方的合约
```

**修复**: CREATE2 的 salt 要足够随机 + 同一地址不可重复部署
**真实案例**: 很多跨链桥的固定地址部署漏洞

---

## 模式 48: delegatecall 代理存储

```
Proxy 合约通过 delegatecall 调用 Logic 合约
delegatecall 在 Proxy 的 storage 上下文中执行
如果 Logic 合约修改了某 storage slot → 实际改的是 Proxy 的

常见问题:
  Proxy.slot[0] = owner
  Logic.slot[0] = tokenBalance
  Logic.setTokenBalance(0) → 改成了 Proxy.owner = 0
```

**修复**: 使用 EIP-1967 标准 storage slots + OpenZeppelin 的 UUPS

---

## 模式 49: 自毁合约

```
合约 A: 使用 address(this).balance 做条件判断
攻击者:
1. 创建一个合约 B, 存入 1 ETH
2. 调用 B.selfdestruct(target = 合约 A)
3. 合约 A 的余额被强制增加 1 ETH
4. 某个原本不应该触发的条件变成了 true
```

**修复**: 不要依赖 address(this).balance 做关键判断
**检查**: 有 `address(this).balance` 出现在 if/require 中吗？

---

## 模式 50: storage 碰撞 (ERC-1967)

```
ERC-1967 定义了标准的 storage slots:
  _IMPLEMENTATION_SLOT = 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc
  _ADMIN_SLOT = 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103

如果 Logic 合约不小心覆盖了这些 slot:
  → Proxy 的 implementation 地址被改变
  → 攻击者可以指向恶意逻辑合约
```

**修复**: Logic 合约不要使用 ERC-1967 的保留 slots
**检查**: 合约是否使用了 `_IMPLEMENTATION_SLOT` 附近的 storage？

---

## ✅ 完成: 18 → 50 模式

| 批次 | 模式 | 覆盖 |
|:--:|:--:|------|
| 你的 | 18 | 基础模式 |
| 第 1 批 | 19-23 | DeFi 核心 |
| 第 2 批 | 24-28 | DeFi 进阶 |
| 第 3 批 | 29-33 | 跨链/MEV |
| 第 4 批 | 34-42 | 跨链/Token |
| 第 5 批 | 43-50 | 高级/修复 |

**你能审的: 简单代币合约、基础借贷协议、AMM、跨链桥、治理协议**
**还不能审的: 复杂的 L2、zk 证明、intent-based 协议**
