# Formal Verification Methods — Comparison

## Three Levels

| | Level 1: Foundry | Level 2: Certora | Level 3: Coq/Lean |
|------|:--:|:--:|:--:|
| 方法 | 随机测试 | SMT 求解 | 互动定理证明 |
| 覆盖率 | 采样 | 全量 | 全量 |
| 证明能力 | 找反例 | 证明安全 | 证明任意属性 |
| 学习曲线 | 低 | 中 | 极高 |
| 速度 | 秒级 | 分钟-小时 | 天-周 |
| 成本 | 免费 | 免费社区版 | 免费 |
| 谁在用 | — | Aave, Maker, Lido | 学术研究 |

## When to Use What

- **Foundry invariants**: 每份审计都要写。找 bug 最快。
- **Certora**: 核心不变量需要数学保证。证明后永远不需要再手工检查。
- **Coq**: 协议价值 >$10B 且人命攸关（DeFi 通常不需要这个层级）。

## Files

| 文件 | 内容 |
|------|------|
| `CherumInvariants.sol` | Foundry 不变式测试 |
| `CherumCertora.spec` | Certora CVL 形式化规范 |
