# Chapter 1: Why DeFi Keeps Breaking

## The Numbers

From 2017 to 2026, DeFi protocols lost over **$8 billion** to exploits. The largest single incident (Ronin Bridge) took $625 million. The most common attack vector (flash loans) didn't exist before 2020.

But the raw numbers hide a more important pattern: **DeFi is getting safer AND more dangerous at the same time.**

## The Hardening Gradient

Large protocols ($1B+ TVL) have become remarkably secure. Aave, Uniswap, Maker — each has survived dozens of attack attempts. They've invested millions in audits, bug bounties, and formal verification.

Meanwhile, small protocols (<$10M TVL) are being exploited at an accelerating rate. The attackers have gotten smarter, but the defenders haven't scaled.

This creates a "hardening gradient":
- Top 10 protocols: 0 major exploits since 2023
- Protocols ranked 50-100: exploited weekly
- New protocols launched this month: 30% will be exploited within 90 days

## Why Traditional Security Fails

Blockchain security is fundamentally different from Web2 security:

| Web2 | DeFi |
|------|------|
| You can patch bugs | Code is immutable |
| You can revert transactions | Transactions are final |
| Attackers need infrastructure | Attackers need one transaction |
| Defense scales with money | Defense scales with expertise |
| Bugs cause data leaks | Bugs cause instant fund loss |

When a Web2 company gets hacked, they rotate keys and apologize. When a DeFi protocol gets hacked, the money is gone forever.

## The Attacker's Advantage

Attackers have three structural advantages:

1. **Asymmetric cost**: A single researcher finding one bug can drain an entire protocol. The protocol must prevent ALL bugs. The attacker only needs ONE.

2. **Composability**: DeFi protocols are interconnected. A bug in one contract (e.g., a price oracle) affects every protocol that uses it. Attackers exploit the weakest link in the chain.

3. **Permissionless**: Anyone can deploy any contract. There is no app store review, no security screening. A protocol with zero audits and a $10M TVL is indistinguishable from one with 10 audits and $1B TVL — until it's exploited.

## What This Book Won't Do

This book won't teach you Solidity syntax. It won't explain what a blockchain is. It assumes you already know how to read smart contracts.

What it will do: show you exactly how 105 different attack patterns work, why they keep happening, and how to stop them. Every pattern comes with real-world evidence — the protocol, the date, the dollar amount lost.

## The Only Rule

There is exactly one rule in DeFi security:

> **If your protocol holds value, someone is trying to steal it right now.**

Act accordingly.

---

*Next: Chapter 2 — The Security Researcher's Toolkit*
