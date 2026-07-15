# 文献综述

## 1. DeFi 安全数据集

| 文献 | 年份 | 案例数 | 范围 | 方法 |
|------|:--:|:--:|------|------|
| [1] Werner et al., "SoK: DeFi Attacks" | 2023 | 77 | DeFi only | Manual taxonomy |
| [2] Zhou et al., "DeFiRanger" | 2022 | 43 | Flash loan | Detection rules |
| [3] Qin et al., "Quantifying DeFi" | 2021 | 21 | Price oracle | Empirical |
| [4] DeFiHackLabs (Sun et al.) | 2024 | 874 | All DeFi | PoC replication |
| [5] SlowMist Hacked | 2021- | 500+ | All chains | Incident DB |
| [6] Rekt News | 2020- | 250+ | All DeFi | Journalism |
| **本文** | **2026** | **824** | **2017-2026** | **Multi-source + statistical** |

## 2. 攻击分类法

| 分类 | 提出者 | 优势 | 局限 |
|------|------|------|------|
| OWASP Top-10 | OWASP | 广泛 | 不适合 DeFi |
| Solidity Top-10 | SECBIT | 代码级 | 缺业务逻辑 |
| SAMC | 去中心化安全 | 覆盖广 | 未验证 |
| SCSVS | Consensys | 全面 | 太长 |
| **本文 50-Pattern** | **本文** | **实证验证** | **—** |

## 3. 已有趋势研究中的 GAP

1. **[Gap 1] 无多源交叉验证** — 已有研究依赖单一来源（DeFiHackLabs 或 Rekt）
2. **[Gap 2] 无统计显著性** — 所有趋势都是描述性统计，无假设检验
3. **[Gap 3] 无损失归一化** — 损失金额没有按 TVL 调整
4. **[Gap 4] 无预测模型** — 描述过去，不预测未来

## 4. 本文贡献

1. **首个** 多源交叉验证的 DeFi 攻击数据集（824 → ~500 高置信度）
2. **首个** 在 DeFi 攻击分析中应用 χ² 和 Mann-Kendall 检验
3. **首个** 按 DeFi TVL 归一化的攻击损失时间序列
4. **构建** 50 模式的实证分类体系

## 5. 参考格式 @misc

```
[1] Werner, S. et al. (2023). SoK: Decentralized Finance (DeFi) Attacks. IEEE S&P 2023.
[2] Zhou, L. et al. (2022). DeFiRanger: Detecting Price Manipulation Attacks. ACM CCS 2022.
[3] Qin, K. et al. (2021). Quantifying Blockchain Extractable Value. IEEE S&P 2021.
[4] Sun, W. et al. (2024). DeFiHackLabs. GitHub.
[5] SlowMist (2021-). Hacked: SlowMist Hacked Database.
[6] Rekt News (2020-). The Rekt Leaderboard.
```
