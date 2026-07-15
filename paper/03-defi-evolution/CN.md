# DeFi 攻击演化：十年 824 个安全事件的实证分析

**作者**：陈世强 (Shiqiang Chen) — 独立安全研究员 | **DOI**: 10.5281/zenodo.21382653

---

## 摘要

824 个 DeFi 攻击事件的实证分析。风险指数从 3.33% → 2.33% (↓30%)。

## 风险指数下降

![风险指数](figures/03-defi-evolution/fig1-risk-index.pdf)

*图1: DeFi 年度损失占 TVL 比例。2022 年峰值后持续下降*

## 攻击类别分布

![攻击类别](figures/03-defi-evolution/fig2-categories.pdf)

*图2: 14 个攻击类别的分布 (N=824)。闪贷+价格操纵占 30%*

## 闪贷攻击趋势

![闪贷趋势](figures/03-defi-evolution/fig3-flashloan-trend.pdf)

*图3: 闪贷攻击占比。2023 年达峰值 40.4%，之后下降至 28.4%*

## 代码漏洞 vs 业务逻辑

![代码vs业务](figures/03-defi-evolution/fig4-code-vs-business.pdf)

*图4: 代码级漏洞被工具消除，但业务逻辑漏洞保持不变*

## 结论

- 风险指数 ↓30%：生态在变安全
- 闪贷仍是主要高价值向量
- 重入攻击显著减少（编译器/库默认防护）
- 2026 预测：AI 代理合约、L2 基础设施成为新风险

---

数据集：https://doi.org/10.5281/zenodo.21382653
