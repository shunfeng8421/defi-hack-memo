# Solidity DeFi 漏洞习题集
> 50个实战习题，每个对应一个攻击模式
> 作者: Shiqiang Chen — July 2026

## 习题结构

每个习题包含:
- `contracts/*.sol` — 有漏洞的合约
- `exploit/*.sol` — 攻击合约 (PoC)
- `fix/*.sol` — 修复后的合约
- `README.md` — 习题说明

## 难度分级

| 等级 | 说明 | 数量 |
|:--:|------|:--:|
| ⭐ | 一眼看出 | 10 |
| ⭐⭐ | 需要分析 | 20 |
| ⭐⭐⭐ | 需要组合多个模式 | 15 |
| ⭐⭐⭐⭐ | 接近真实审计难度 | 5 |

## 习题列表 (首批10题)

| # | 习题 | 模式 | 难度 |
|:--:|------|:--:|:--:|
| 01 | FlashLoanOracle | #1 闪贷+预言机 | ⭐⭐ |
| 02 | ReentrancyVault | #2 重入 | ⭐ |
| 03 | InflationDonation | #5 ERC-4626通胀 | ⭐⭐ |
| 04 | GovFlashLoan | #11 闪贷治理 | ⭐⭐⭐ |
| 05 | PrecisionVault | #46 精度损失 | ⭐ |
| 06 | SignatureReplay | #27 签名重放 | ⭐⭐ |
| 07 | CrossChainBridge | #34 跨链重放 | ⭐⭐⭐ |
| 08 | PermitFrontrun | #15 许可前置 | ⭐⭐ |
| 09 | BurnToken | #25 代币燃烧 | ⭐⭐⭐ |
| 10 | UpgradeCollision | #13 升级碰撞 | ⭐⭐⭐ |
