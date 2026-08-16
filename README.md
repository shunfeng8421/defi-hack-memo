[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![DeFi Security](https://img.shields.io/badge/DeFi-Security%20Research-blue)](https://github.com/shunfeng8421/defi-hack-memo)
[![Papers](https://img.shields.io/badge/Papers-9-green)](paper/)
[![Audit Reports](https://img.shields.io/badge/Audit%20Reports-42-orange)](audit-reports/)
[![PoC Exploits](https://img.shields.io/badge/PoC%20Exploits-21-red)](exploits/)
[![CVE](https://img.shields.io/badge/CVE-38%20Findings-purple)](cve/)

# 10-security — DeFi 安全研究知识库

> **Shiqiang Chen | shunfeng8421 | 38 安全发现 | 9 论文 | 58 检测规则**

## 快速导航
| DeFi 安全手册 | [handbook/](handbook/) — 14章, ~18,000词 |

| 你想找 | 去哪 |
|------|------|
| 论文 | [paper/](paper/) — 9篇, 按编号 01-09 |
| 审计报告 | [audit-reports/](audit-reports/) — 42份 |
| 攻击案例 | [cases/](cases/) — 824 DeFiHackLabs 案例 |
| 攻击链分析 | [attack-chains.md](attack-chains.md) — 20个完整还原 |
| 漏洞利用 | [exploits/](exploits/) — 21 PoC脚本 |
| CVE 记录 | [cve/](cve/) — 38安全发现汇总 |
| 练习题 | [exercises/](exercises/) — Solidity + 区块链模块 |
| PoC 项目 | [pocs/](pocs/) — Foundry PoC + AI钱包 |
| 工作日志 | [daily-logs/](daily-logs/) — 每日记录 |

## 论文 × 发现交叉引用

| 论文 | 验证发现 |
|------|------|
| #01 Prompt Injection × MCP | CherryStudio CVE×2 |
| #04 十年分析 | Truebit, SummerFi 等 10+ |
| #06 50模式分类学 | 23 个发现, 14 种模式 |
| #07 硬化梯度 | SummerFi (后预言机时代) |
| #08 EIP-712 错误 | giddy, BossBridge, Snowman, PresidentElector |
| #09 AI Agent × DeFi | Clicks, Cairn, PropFund, AgentPM |

## 搜索关键词

- `EIP-712` → paper/08, audit-reports/giddy*, bossbridge*
- `闪贷` → attack-chains.md #5-8, paper/05
- `跨链` → attack-chains.md #17-18, exercises/bridge/
- `Solana` → defi-scanner.py #51-58, audit-reports/budgent*
- `Python 扫描器` → defi-scanner.py, ai-agent-scanner.py, master-scanner.py
- `AI Auditor` → ai-auditor.py, ai-auditor-llm.py, auditor.html
