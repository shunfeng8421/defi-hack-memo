# DeFi Security Handbook

> **A Field Manual for Smart Contract Security Researchers**
> 66 Attack Patterns. 24 Chapters. 12 Domains. 58 Automated Detection Rules. 824 Real-World Exploit Reports Analyzed.

**Author**: Shiqiang Chen (陈世强)
**Status**: ✅ Complete (24/24 chapters)
**Test Suite**: 105 Foundry fork tests | **Scanner**: 58 automated patterns

---

## 序言

2021年3月，PancakeBunny被盗走600万美元。攻击者没有找合约漏洞。没有绕过权限检查。没有破解私钥。他只做了三件事：借一笔闪电贷，砸进一个交易对，然后取走所有钱。整个攻击持续了七秒钟。

当时我在想一个问题：**为什么一个审计过的协议，会被如此简单的方法攻破？**

答案不是代码有bug。代码逻辑完全正确。`getReserves()`返回的是真实的储备量，除法运算精确到小数点后18位，转账没有越权。问题在于：**代码逻辑正确的边界，不等于真实世界的安全边界。** 在测试环境里，没有人能操纵价格，所以这个函数是安全的。在主网上，有人可以，所以这个函数是致命的。

这个洞察驱动了本书的写作。DeFi安全的本质问题不是代码质量——Solana的Move、以太坊的Solidity，语言的差异远不如思维模型的差异重要。本质问题是：**攻击者和开发者看到的不是同一个系统。** 开发者看到的是自己写的合约。攻击者看到的是整个生态——包括你的合约、Uniswap的流动性、Chainlink的更新间隔、跨链桥的验证逻辑、用户的交易习惯、Gas拍卖的博弈均衡。你把门锁在屋子里，他从不走门。

过去五年，我分析了824份DeFi攻击报告。我发现一个规律：**大多数漏洞不是新颖的。它们是已知模式的变形。** 闪电贷+现货价格预言机、跨链消息重放、未验证的oracle返回值、初始化函数无保护——这些模式反复出现，每次换一个协议名字，每次多几个受害者。

所以这本书的做法不同。不是按照漏洞类型分类，而是按照攻击模式分类。每个模式都配真实的案例、真实的代码、真实的修复方案，以及在主网上可以跑通的Foundry分叉测试。你不是在读理论，你是在看犯罪现场还原。

这本书也不是一本中立的教科书。它有立场：**安全知识应该是免费的。** 顶级协议的审计预算动辄百万美元，但那些最需要安全知识的——早期项目方、个人开发者、Web3创业者——反而最缺乏获取渠道。硬化梯度（第一章）讲的就是这个悖论：越大的协议越安全，越小的协议越危险，而DeFi的创新恰恰来自后者。

如果你是一个审计师，这本书应该成为你的随身清单。如果你是一个协议开发者，第一章值得你反复读——它解释的不是你的代码为什么会有bug，而是你的协议为什么会被选中成为目标。如果你是一个安全研究员，第二十二章的扫描器和第二十三章的测试框架可以省你三个月的时间。

这本书不保证你读完就能发现所有的漏洞。它只保证一件事：**读完以后，你不会再对任何一份审计报告上的"Low Risk"掉以轻心。**

2026年7月，深圳

---

## Preface

In March 2021, PancakeBunny lost $6 million. The attacker found no contract bug. No permission bypass. No stolen private key. He did three things: took a flash loan, dumped it into a liquidity pool, and withdrew everything. The entire attack lasted seven seconds.

At the time, I kept asking myself: **how could an audited protocol be broken so simply?**

The answer was not a code bug. The logic was flawless. `getReserves()` returned real reserves. The division was precise to 18 decimal places. The transfer had no permission error. The problem was: **the boundary where code is logically correct is not the boundary where the system is secure.** In a test environment, no one could manipulate the price, so the function was safe. On mainnet, someone could, so the function was fatal.

This insight drives the entire book. The essence of DeFi security is not code quality—Solana's Move, Ethereum's Solidity, the language matters far less than the mental model. The real issue is: **attackers and developers see different systems.** The developer sees their own contract. The attacker sees the entire ecosystem—your contract, Uniswap's liquidity, Chainlink's update intervals, cross-chain bridge verification, user trading patterns, gas auction equilibria. You lock the door inside the house. He never comes through the door.

Over five years, I analyzed 824 DeFi exploit reports. One pattern emerged: **most vulnerabilities are not novel. They are variations of known patterns.** Flash loan + spot price oracle. Cross-chain message replay. Unverified oracle returns. Unprotected initializer functions. These patterns repeat, each time with a different protocol name, each time with more victims.

This book takes a different approach. It classifies by attack pattern, not vulnerability type. Every pattern comes with a real case, real code, a real fix, and a Foundry fork test that runs on mainnet state. You are not reading theory. You are reading crime scene reconstructions.

This book is also not neutral. It has a position: **security knowledge should be free.** Top protocols spend millions on audits, but those who need security knowledge most—early-stage teams, independent developers, Web3 founders—have the least access. The hardening gradient (Chapter 1) describes precisely this paradox: larger protocols become more secure, smaller protocols become more dangerous, and DeFi innovation comes from the latter.

If you are an auditor, this book should be your field checklist. If you are a protocol developer, Chapter 1 is worth reading repeatedly—it explains not why your code has bugs, but why your protocol will be chosen as a target. If you are a security researcher, Chapter 22's scanner and Chapter 23's testing framework will save you three months of work.

This book does not guarantee you will find every vulnerability. It guarantees one thing: **after reading it, you will never again dismiss a "Low Risk" finding on an audit report.**

July 2026, Shenzhen

---

## What This Book Is

This is a **field manual**, not a textbook. It assumes you can read Solidity and understand basic DeFi primitives. It focuses on what breaks, how it breaks, why it was allowed to break, and how to prevent it from breaking again.

Every vulnerability pattern includes:
- **The Attack**: Real-world case with dollar amount
- **The Code**: Vulnerable Solidity + the fix
- **The Why**: Root cause analysis — why did this ship to production?
- **The Check**: Scanner detection logic for automated finding

---

## How to Use This Book

**If you are an auditor**: Read Part I for the mental model, then use Part II as a checklist on every engagement.

**If you are a protocol developer**: Read Chapter 1 to understand why your protocol will be attacked, then read every chapter that matches your architecture.

**If you are a security researcher**: Read front to back. The patterns compound.

---

## Table of Contents

### Part I: Foundations (Chapters 1-3)

| Ch | Title | Status |
|:--:|-------|:------:|
| 1 | [Why DeFi Keeps Breaking](part1/ch01-why-defi-breaks.md) | ✅ |
| 2 | [The Security Researcher's Toolkit](part1/ch02-toolkit.md) | ✅ |
| 3 | [How to Read an Exploit Report](part1/ch03-reading-exploits.md) | ✅ |

### Part II: 37 Core EVM Patterns (Chapters 4-12)

| Ch | Title | Patterns | Status |
|:--:|-------|:--------:|:------:|
| 4 | [Flash Loan Attacks](part2/ch04-flash-loans.md) | #1-3 | ✅ |
| 5 | [Oracle Manipulation](part2/ch05-oracle-manipulation.md) | #4-8 | ✅ |
| 6 | [Access Control Failures](part2/ch06-access-control.md) | #9-12 | ✅ |
| 7 | [Token Economics Attacks](part2/ch07-token-economics.md) | #13-16 | ✅ |
| 8 | [Cross-Chain Vulnerabilities](part2/ch08-cross-chain.md) | #17-20 | ✅ |
| 9 | [Reentrancy & Callback Attacks](part2/ch09-reentrancy.md) | #21-24 | ✅ |
| 10 | [Initialization & Upgrade Attacks](part2/ch10-initialization.md) | #25-28 | ✅ |
| 11 | [Precision, Arithmetic & Gas](part2/ch11-precision-gas.md) | #29-33 | ✅ |
| 12 | [Governance & Admin Attacks](part2/ch12-governance.md) | #34-37 | ✅ |

### Part III: Solana Security (Chapter 13)

| Ch | Title | Patterns | Status |
|:--:|-------|:--------:|:------:|
| 13 | [The Account Model Attack Surface](part3/ch13-solana.md) | #51-56 | ✅ |

### Part IV: Domain Extensions (Chapters 14-21)

| Ch | Title | Patterns | Status |
|:--:|-------|:--------:|:------:|
| 14 | [MEV & Front-Running](part4/ch14-mev-frontrunning.md) | #38-42 | ✅ |
| 15 | [Lending Protocol Attacks](part4/ch15-lending-protocol-attacks.md) | #43-46 | ✅ |
| 16 | [DEX Concentrated Liquidity](part4/ch16-dex-concentrated-liquidity.md) | #47-49 | ✅ |
| 17 | [DePIN Physical-Layer Attacks](part4/ch17-depin-physical-layer.md) | #50-53 | ✅ |
| 18 | [ZK Circuit Vulnerabilities](part4/ch18-zk-circuit.md) | #54-57 | ✅ |
| 19 | [RWA Tokenization Risks](part4/ch19-rwa-tokenization.md) | #58-60 | ✅ |
| 20 | [GameFi Economic Attacks](part4/ch20-gamefi-economics.md) | #61-63 | ✅ |
| 21 | [AI Agent Security](part4/ch21-ai-agent-security.md) | #64-66 | ✅ |

### Part V: Defense (Chapters 22-24)

| Ch | Title | Status |
|:--:|-------|:------:|
| 22 | [Building a Security Scanner](part5/ch22-security-scanner.md) | ✅ |
| 23 | [Writing Effective Fork Tests](part5/ch23-writing-effective-tests.md) | ✅ |
| 24 | [Incident Response Checklist](part5/ch24-incident-response.md) | ✅ |

### Appendices

| App | Title |
|:---:|-------|
| A | [Complete Pattern Reference](appendix/A-complete-pattern-reference.md) |
| B | [Real-World Loss Database](appendix/B-real-world-loss-database.md) |
| C | [Foundry Test Suite Quick Start](appendix/C-foundry-test-suite.md) |
| D | [Scanner Configuration Guide](appendix/D-scanner-configuration.md) |

---

## Design Principles

1. **Every pattern is backed by a real case.** No hypotheticals. Every vulnerability description includes at least one protocol that lost real money.

2. **Every pattern has three parts**: Vulnerability Code → Attack Description → Fix. You should be able to use this as an audit checklist.

3. **Root cause comes first.** "What happened" is easy. "Why it was allowed to happen" is the question that separates junior researchers from senior ones.

4. **The scanner is a teaching tool.** The 66-pattern classification maps to 58 automated detection rules in the companion scanner (`defi-scanner.py`). Some attack classes (MEV, social engineering, consensus-layer attacks) resist automated detection and require the manual methodology described in their respective chapters.

---

*Last updated: 2026-07-25*
