# DeFi 核心漏洞 — 第 4 批 (模式34-42)

## 模式 34: 跨链消息重放

```
攻击者在 Chain A 发一笔跨链请求
验证器签名通过 → 在 Chain B 执行
攻击者复制同一请求在 Chain C 再次执行
→ 一份资产在多个链上被铸造
```

**修复**: 消息中包含 `chainID`（EIP-155）+ `nonce`
**检查**: execute() 函数是否验证了 `block.chainid`？

---

## 模式 35: 轻客户端欺骗

```
跨链桥使用轻客户端验证另一条链的区块头
攻击者构造一个"伪造的区块头"让轻客户端验证通过
→ 伪造的提现请求被当作有效跨链消息处理
```

**修复**: 验证区块头的难度/工作量、多验证器共识
**真实案例**: 2022 Wormhole $320M（签名验证漏洞）

---

## 模式 36: 中继器作恶

```
跨链桥依赖中继器(node/relayer)传递消息
恶意中继器可以:
1. 不转交消息（审查）
2. 延迟转交（操纵价格窗口）
3. 修改消息内容（如果有签名漏洞）
```

**修复**: 消息签名 + 多路径传递 + 超时检测

---

## 模式 37: 存款/铸币不匹配

```
Chain A: 用户存 123.456 ETH
Chain B: 铸币 123 ETH（精度截断）
→ 用户损失 0.456 ETH/次
→ 多次操作即可提取合约的沉淀资金
```

**修复**: 精度对齐 + 四舍五入处理

---

## 模式 38: 捐赠攻击 (Inflation)

```
AMM 池:
攻击者直接向池合约转账 → 不调用 swap()
池子的 totalSupply 不变但 balanceOf 增加
下一个存款者获得异常的 LP 份额
```

**修复**: 用内部 accounting 变量（如 `_totalLiquidity`）代替 `address(this).balance`

---

## 模式 39: TWAP 周期不足

```
TWAP 取最近 N 个区块的平均价格
如果周期太短（如 10 个区块 ≈ 2 分钟）
攻击者可以持续操纵价格 N 个区块
成本 = N × 区块奖励 + 滑点
仍然可能有利润
```

**标准**: TWAP 周期 >= 30 分钟（约 150 个区块）
**检查**: oracle.period() 是否 >= 1800？

---

## 模式 40: ERC-4626 共享攻击 (升级)

```
Vault 使用 share 概念
攻击者:
1. 少量 deposit 获得 share
2. 直接 transfer 资产到 vault（不调用 deposit）
3. share 变多 → 下一个用户的存款被稀释
```

**修复**: 首次存款时预铸一定数量的 share 作为防护

---

## 模式 41: ERC-721 safeTransferFrom 重入

```
safeTransferFrom 会调用接收合约的 onERC721Received
如果攻击合约的 onERC721Received 再次调用 transferFrom
→ 同一个 NFT 被转出两次
```

**修复**: 先更新 owner 再调用 safeTransferFrom
**检查**: transferFrom 前是否更新了 `_owners` 映射？

---

## 模式 42: ERC-1155 batch 重入

```
safeBatchTransferFrom 批量转账
如果任意一个接收者的回调合约包含恶意代码
→ 可以中断或修改正在执行的批量转账
```

**修复**: checks-effects-interactions + 非重入锁
