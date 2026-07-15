# Deep Case Studies: 5 Landmark DeFi Attacks

## Case 1: bZx (2020) — The First Flash Loan Attack

**损失**: $50M | **模式**: P1 (闪贷+价格操纵)

### 攻击链

```
Step 1: 闪电贷借 10,000 ETH (≈$2M, 来自 dYdX)
Step 2: 在 Uniswap 用 ETH 换 WBTC → 拉高 WBTC 价格
Step 3: 被攻击合约 (bZx) 用这个扭曲的价格评估抵押品
Step 4: 抵押品"看起来"价值极高 → 借出远超应有价值的稳定币
Step 5: 还闪电贷 → 净赚 $350K 利润
```

### 为什么 bZx 被攻击

```solidity
// bZx 的预言机获取价格:
function getPrice(address token) returns (uint) {
    // ❌ 从 Uniswap 直接获取瞬时价格
    return uniswapPair.getReserves();
    // 攻击者在同一笔交易中操纵了 reserves
}
```

### 历史意义

这是**首次**将闪电贷武器化的攻击。在 bZx 之前，闪电贷被认为只是"无风险套利"工具。bZx 证明了：**任何使用瞬时价格的 DeFi 协议都可以在 13 秒内被摧毁。**

bZx 被连续攻击了 **3 次**（2 月、9 月的 3 次事件），每次都是同一个模式的不同变种。这证明了自动化审计的必要性——如果 bZx 在第一次攻击后进行了安全审计，后两次攻击可以避免。

---

## Case 2: Cream Finance (2021) — Triple Exploit

**损失**: $130M | **模式**: P1 + P2 + P11 (闪贷+重入+治理)

### 攻击链

```
Step 1: 闪电贷借 500M AMP 代币 (价值 $25M)
Step 2: 将 AMP 存入 Cream 作为抵押品
Step 3: AMP 的 ERC-777 "tokensToSend" 回调被触发
Step 4: 回调中再次调用 Cream 的借贷函数 → 重入
Step 5: 重入过程中, Cream 的余额计算被绕过
Step 6: 借出 $130M 的 ETH 和其他代币
Step 7: 提取抵押的 AMP → 还闪电贷 → 净赚
```

### 为什么 Cream 被攻击

1. **ERC-777 回调机制**: tokensToSend 回调在转账前触发，给了攻击者在状态更新前的执行窗口
2. **重入保护不足**: Cream 的 borrow 函数没有检查余额是否已被更新
3. **攻击者发现了 3 个模式的组合**: 这不是单一的代码漏洞，而是闪贷→代币特性→重入的三重路径

### 为什么是经典案例

Cream 证明了一个关键安全原则：**安全的单个组件组合后不一定安全。** Cream 用了 OpenZeppelin 库、有审计报告——但 ERC-777 + 闪贷 + AMM 三个"安全"组件的组合产生了致命漏洞。

---

## Case 3: Poly Network (2021) — 里程碑式跨链攻击

**损失**: $610M | **模式**: P34 (跨链签名) + P37 (权限漏洞)

### 攻击链

```
Step 1: 攻击者找到 EthCrossChainManager 合约
Step 2: 合约有一个 "keeper" 角色可以修改关键参数
Step 3: 攻击者通过 verifyHeaderAndExecuteTx 函数
        传入精心构造的参数
Step 4: 参数使得合约误认为攻击者是 keeper
Step 5: 攻击者将跨链消息的接收方设为自己的地址
Step 6: $610M 从 Ethereum、BSC、Polygon 三条链被同时提走
```

### 核心漏洞

```solidity
function verifyHeaderAndExecuteTx(...) returns (bool) {
    // ❌ 无 caller 验证 — 任何人可以传入任意参数
    // ❌ 无 chainID 检查 — 同一消息可被重放到其他链
    // ❌ 无 nonce 去重 — 同一消息可被多次执行
    
    require(_verifyHeader(proof, rawHeader, headerProof, curRawHeader, headerSig));
    _executeCrossChainTx(toContract, toChainId, txData);
}
```

### 历史意义

$610M 是当时（2021年）最大的 DeFi 攻击。但结局出人意料：攻击者将**全部资金归还**，声称是"为了系统安全而进行的白帽测试"。这个故事成为 DeFi 安全社区的传奇，也推动了跨链桥安全模型的根本性变革。

---

## Case 4: Euler Finance (2023) — 借贷协议的精准打击

**损失**: $197M | **模式**: P6 (借贷清算)

### 攻击链

```
Step 1: 攻击者通过两次大额操作"欺骗" Euler 的健康因子计算
Step 2: 攻击者在其他协议中触发强制清算
Step 3: Euler 的清算逻辑依赖外部调用
Step 4: 攻击者用闪电贷创建了看似"健康"的借贷头寸
Step 5: 清算被绕过 → 攻击者提取超出抵押品的资产
```

### 技术细节

Euler 的 donateToReserves 函数在处理捐赠时改变了 eToken 的 exchange rate。攻击者通过大量捐赠 + 借贷操作，利用了 exchange rate 计算中的精度偏移。

```solidity
// Euler 的 exchange rate 计算:
uint newExchangeRate = (totalBorrows + reserveBalance) * 1e18 / totalSupply;
// ↑ 如果 totalBorrows 和 reserveBalance 可以被操纵
// → exchangeRate 被扭曲 → 抵押品估值错误
```

### 结局

攻击者最终归还了全部 $197M 资金，并与 Euler 团队合作修复了漏洞。这是 DeFi 历史上白帽转换最成功的案例之一。

---

## Case 5: Bybit (2025) — 社交工程 + 代理升级

**损失**: $1.5B | **模式**: P37 (权限) + P48 (代理升级)

### 攻击链

```
Step 1: 攻击者通过社交工程获取 Bybit 多签钱包访问权
Step 2: Bybit 的 ETH 冷钱包使用了 Safe (原 Gnosis Safe) 多签
Step 3: 攻击者构造了一个"看似正常"的代理升级交易
Step 4: 3/6 多签者被诱骗签署了恶意交易
Step 5: 代理合约的 implementation 被改为攻击者控制的后门合约
Step 6: $1.5B 的 ETH 在几分钟内被转出
```

### 为什么不是"代码漏洞"而是"过程漏洞"

Bybit 使用的 Safe 多签合约本身是安全的。漏洞出在：
1. 多签者没有仔细审查签名的交易内容
2. Safe 的交易展示 UI 被前端篡改
3. 代理升级没有额外的安全边界

这标志着 DeFi 安全从"保护代码"进入了"保护过程"的新阶段。

---

## 五个案例的共同模式

| 案例 | 链 | 根本原因 | 可以被自动化审计发现吗？ |
|:----:|:--:|------|:--:|
| bZx | ETH | 瞬时价格 | ✅ getReserves() → ❌ |
| Cream | ETH | 组件交互 | ⚠️ 组合模式检测 |
| Poly | Multi | 权限缺失 | ⚠️ 需要分析整个调用链 |
| Euler | ETH | 精度 + 捐赠 | ⚠️ 需要理解业务逻辑 |
| Bybit | ETH | 过程漏洞 | ❌ 无法 (不是代码漏洞) |

**结论**: 随着 DeFi 安全成熟，**纯代码漏洞在减少，业务逻辑和过程漏洞在增加。** 这也解释了为什么自动化审计不能完全替代人工审计。
