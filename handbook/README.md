# DeFi Security Handbook

## 105 Attack Patterns Across 17 Domains

**Author**: Shiqiang Chen · Independent Security Researcher
**Repository**: github.com/shunfeng8421/defi-hack-memo
**Status**: First Edition · July 2026

---

## About This Book

This handbook is the result of systematically analyzing 824 DeFi exploit reports spanning from 2017 to 2026. Every attack pattern has been verified against real-world protocol losses totaling over $1.05 billion. Every pattern has an executable Foundry test that anyone can run, verify, and learn from.

This is not an academic paper. This is a field manual for security researchers, auditors, and protocol developers who need to understand what breaks and why.

---

## Table of Contents

### Part I: Foundations
1. [Why DeFi Keeps Breaking](part1/ch01-why-defi-breaks.md)
2. [The Security Researcher's Toolkit](part1/ch02-toolkit.md)
3. [How to Read an Exploit Report](part1/ch03-reading-exploits.md)

### Part II: The 50 Core DeFi Patterns
4. Flash Loan Attacks (Patterns 1-4)
5. Oracle Manipulation (Patterns 5-8)
6. Access Control Failures (Patterns 9-14)
7. Token Economics (Patterns 15-18)
8. Cross-Chain Vulnerabilities (Patterns 19-22)
9. Reentrancy & Callbacks (Patterns 23-27)
10. Initialization & Upgrades (Patterns 28-32)
11. Precision & Arithmetic (Patterns 33-36)
12. DoS & Griefing (Patterns 37-42)
13. Gas & Storage (Patterns 43-48)
14. Governance & Admin (Patterns 49-50)

### Part III: Solana Security (Patterns 51-58)
15. Account Model Vulnerabilities
16. CPI & PDA Attacks

### Part IV: Domain Extensions (Patterns 59-105)
17. Bridge Security
18. Proxy Upgrade Attacks
19. MEV & Frontrunning
20. Governance Exploits
21. Lending Protocol Attacks
22. DEX Concentrated Liquidity
23. DePIN Physical-Layer Attacks
24. ZK Circuit Vulnerabilities
25. RWA Tokenization Risks
26. GameFi Economics
27. AI Agent Security
28. NFT Protocol Attacks
29. Stablecoin Design Flaws
30. Wallet Infrastructure
31. Privacy Protocol Weaknesses
32. Yield Aggregator Pitfalls

### Part V: Defense
33. Building a Security Scanner
34. Writing Effective Tests
35. Incident Response Checklist

### Appendices
- A: Complete Pattern Reference (105 patterns)
- B: Real-World Loss Database ($1.05B across 100 incidents)
- C: Foundry Test Suite Quick Start
- D: Scanner Configuration Guide

---

## How to Use This Book

**If you're an auditor**: Start with Part II. Run the Foundry tests. Every pattern has code you can copy into your audit checklist.

**If you're a developer**: Read the chapter that matches your protocol type. The "Fix" section in every pattern tells you exactly what to change.

**If you're a researcher**: The appendices are your data. 824 incidents, 105 patterns, 100 confirmed findings with dollar amounts.

---

## License

CC BY 4.0 — Free to share, adapt, and use. Attribution required.

---

*"Security is not a feature. It is the absence of known vulnerabilities, continuously verified."*
