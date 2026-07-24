# Part IV & V — Writing Plan

## Quality Standard

每章必须有：

| 要素 | 最低要求 |
|------|------|
| 开篇案例 | 真实攻击，有金额，有叙事 |
| 深度代码 | 漏洞代码 + 修复代码，至少 3 个完整示例 |
| 模式编号 | 明确对应 105 模式中的编号 |
| 检测方法 | 扫描器如何发现这个模式 |
| 检查清单 | 3-7 条可执行检查项 |
| 最低字数 | **1,500+** 英文词（不含代码块） |

## Part IV —— 领域扩展

### Ch14: MEV & Front-Running
- 开篇案例: makina $5.1M（MEV 反杀）
- 模式: Sandwich Attack · Just-In-Time Liquidity · Time-Bandit · Multi-Block MEV · MEV Bot Replay
- 代码: 有漏洞的 AMM swap + MEV 攻击合约
- 亮点: MEV 是 DeFi 安全研究的盲区——大多数审计不检查

### Ch15: Lending Protocol Attacks
- 开篇案例: RadiantCapital $4.5M
- 模式: Bad Debt Accumulation · Liquidation Front-Running · Price Oracle Drift · Non-Liquidatable Collateral · Rounding Exploit
- 代码: Compound fork 漏洞 + 修复

### Ch16: DEX Concentrated Liquidity
- 开篇案例: Uniswap V3 tick 操纵
- 模式: Tick Boundary · Just-In-Time Liquidity · Range Order Sandwich · Fee Tier Abuse
- 代码: V3 pool 状态 + tick 数学

### Ch17: DePIN Physical-Layer Attacks
- 开篇案例: Helium 位置欺骗
- 模式: GPS Spoofing · Storage Proof Forgery · Bandwidth Inflation · Sensor Manipulation
- 代码: Proof-of-Coverage 验证逻辑

### Ch18: ZK Circuit Vulnerabilities
- 开篇案例: 未约束信号导致证明伪造
- 模式: Missing Constraint · Overflow Wrapping · Trusted Setup Leak · Input Forgery · Recursive Amplification
- 代码: Circom 电路 + 漏洞

### Ch19: RWA Tokenization Risks
- 开篇案例: 托管人破产导致代币归零
- 模式: Double-Minting · Compliance Bypass · Custody Failure · Redemption Run · Jurisdiction Arbitrage
- 代码: 代币化合约的托管验证逻辑

### Ch20: GameFi Economics
- 开篇案例: Axie Infinity 死亡螺旋
- 模式: RNG Manipulation · Reward Loop Exploit · Bot Farming · NFT Duplication · Governance Capture
- 代码: 随机数生成 + 经济模型

### Ch21: AI Agent Security
- 开篇案例: CherryStudio MCP CVE（你的原创）
- 模式: Prompt Injection · Output Exploitation · Tool Call Hijacking · MCP Server Poisoning
- 代码: Prompt 注入测试框架

## Part V —— Defense

### Ch22: Building a Security Scanner
- 开篇案例: 58 模式扫描器的架构
- 内容: 模式设计 · False Positive 控制 · JSON 输出格式 · CI 集成

### Ch23: Writing Effective Tests
- 开篇案例: 105 模式 Foundry 测试套件
- 内容: CEI 模式 · Fork Testing · Fuzzing · 攻击模拟

### Ch24: Incident Response
- 开篇案例: 你的 4 封 Bug Bounty 邮件实战
- 内容: 检测 · 响应 · 沟通 · 修复 · 披露

### Appendices
- A: 105 Pattern Quick Reference
- B: 100 Exploit Database
- C: Scanner Rules Reference
- D: Test Suite Quick Start

---

## Tomorrow's Plan

| 时间段 | 章节 | 预估字数 |
|------|------|--:|
| 上午 | Ch14 MEV + Ch15 Lending | 3,000-4,000 |
| 中午 | Ch16 DEX + Ch17 DePIN | 3,000-4,000 |
| 下午 | Ch18 ZK + Ch19 RWA | 3,000-4,000 |
| 晚上 | Ch20 GameFi + Ch21 AI | 3,000-4,000 |
| 收尾 | Part V Defense (3章) + Appendices | 4,000+ |

**目标: 明天完成全书 24 章 + 4 附录，总字数 35,000+**
