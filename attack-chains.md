# 20 Attack Chain Forensics — Complete Archive

## EIP-712 系列 (4)
1. **giddyvaultv3 $1.3M** — TYPEHASH 排除 struct 字段 → 签名复用
2. **BossBridge** — 无 nonce/chainId/deadline → 签名重放
3. **SnowmanAirdrop** — "addres" 拼写错误 → 签名永不匹配
4. **PresidentElector** — uint256[] vs address[] type mismatch

## 闪贷/预言机 (4)
5. **PancakeBunny $120M** — 即时价格预言机 → 巨量铸币
6. **Truebit $25M** — Bonding Curve 无冷却期 → 反复套利
7. **WhalebitDeFi $824K** — Algebra V3 即时价格
8. **CurveLlamaLend $240K** — 闪贷操纵清算阈值

## 会计/精度 (3)
9. **SummerFi $6M** — NAV = Σ Ark.totalAssets() — 脱锚代币当$1算
10. **ThetanutsFi $2.1M** — totalSupply=3 wei → 除零免费铸币
11. **futureswap $394K** — feeRateWad 解读为 bps → 10000x误差

## 权限/访问控制 (3)
12. **TrustedVolumes $5.87M** — 注册无权限 + 查错 Key 双 Bug 链
13. **NewMarketTrading $3.98M** — Axelar Express 路径 + Safe Module
14. **DxSale $7.3M** — 89钱包269天隐藏 owner → 慢性后门

## 多池操纵 (2)
15. **makina $5.1M** — DUSD+MIM 双池操纵, MEV 抢跑攻击者
16. **BCE Token $800K** — scheduledDestruction + sync() 价格崩盘

## ZK/跨链 (2)
17. **VerusBridge $11.6M** — Merkle 证明可伪造 → 无锁仓铸币
18. **AztecConnect $2.19M** — numRealTxs 不匹配 → ZK 证明绕过

## 借贷/清算 (2)
19. **BlueberryProtocol $1.4M** — enterMarkets() + 白帽救援
20. **TOPBPool $1.8M** — 治理投票操纵 + Balancer 池清空

---

**总计**: 20 攻击链 | $350M+ 损失 | 14 种漏洞模式 | 全链上还原
