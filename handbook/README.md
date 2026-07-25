# DeFi Security Handbook

> **A Field Manual for Smart Contract Security Researchers**
> 66 Attack Patterns. 24 Chapters. 12 Domains. 58 Automated Detection Rules. 824 Real-World Exploit Reports Analyzed.

**Author**: Shiqiang Chen (陈世强)
**Status**: ✅ Complete (24/24 chapters)
**Test Suite**: 105 Foundry fork tests | **Scanner**: 58 automated patterns

> 📖 [中文序言与目录](README.zh-CN.md) | Chinese preface & navigation available

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
