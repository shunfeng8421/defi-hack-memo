# Formal Verification — From Audit to Proof

## Why Formal Verification

| 方法 | 能做什么 |
|------|------|
| 手动审计 | "我看完了代码，没找到明显的漏洞" |
| 扫描器 | "58 个已知模式都没有匹配到" |
| 单元测试 | "这 100 个特定输入都通过了" |
| Fuzz 测试 | "这个函数在 10,000 个随机输入下都通过了" |
| **不变式测试** | "经过任意顺序的有效操作后，协议属性仍然成立" |
| **数学证明** | "在所有可能的输入和状态下，属性永远成立" |

## 入门路径

### Level 1: Foundry 不变式测试 (今天完成)
- 写 handlers 模拟所有可执行的操作
- 写 invariants 表达协议属性
- `forge test` 自动 fuzz，找到违反不变式的序列

### Level 2: Certora Prover
- 安装 Certora CLI
- 写 CVL 规范 (类似上面的 invariant，但用数学公式)
- Certora 用 SMT 求解器**证明**不变量对所有输入成立

### Level 3: Coq/Lean
- 写形式化机器可检查的证明
- 比 Certora 更底层，可以证明更复杂的属性
- 但需要深厚的数理逻辑基础

## Cherum 不变式

| ID | 不变式 | 类型 |
|:--:|------|------|
| I1 | 每个 nonce 最多处理一次 | 安全 |
| I2 | 目标链铸造量 ≤ 源链销毁量 | 经济 |
| I3 | 暂停时无状态变更 | 活性 |
| I4 | 可用余额 = 总余额 - 停泊金额 | 会计 |

## 运行

```bash
forge test --match-contract CherumInvariants -vvvv
```
