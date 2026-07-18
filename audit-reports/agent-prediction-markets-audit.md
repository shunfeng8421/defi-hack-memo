# Agent Prediction Markets — AI Agent × Oracle Security Audit

**Auditor**: Shiqiang Chen | **Date**: July 18, 2026  
**Project**: agent-prediction-markets-base | **Contracts**: 8 files

## Executive Summary

AI agents create and resolve prediction markets. The oracle resolution system allows trusted agents to vote on outcomes — but reputation can be gamed, and the owner has ultimate override.

| # | Finding | Severity | AI Attack Vector |
|:--:|------|:--:|------|
| 1 | Owner bypasses oracle trust — centralized resolution | 🔴 CRITICAL | Vector #4: MCP MITM |
| 2 | Reputation-weighted voting can be gamed | 🟠 HIGH | Vector #7: Context Poisoning |
| 3 | Auto-vote for high-reputation proposers | 🟡 MEDIUM | Vector #6: Collusion |

## Finding 1: Owner Can Bypass Oracle Trust

**Line**: 91

```solidity
require(trustedOracles[msg.sender] || msg.sender == owner(), "Not trusted oracle");
```

### Description
The contract owner can propose AND finalize any market resolution without being a trusted oracle. This means a single compromised key = all prediction markets can be controlled.

### AI Agent Impact
This is our **Vector #4 (MCP MITM)** in the worst case. If the MCP server that the owner's AI uses is compromised, the attacker can:
1. Place large bets on prediction markets
2. Use owner key to resolve markets in their favor
3. Profit from all agent-predicted outcomes

---

## Finding 2: Reputation Gaming

**Lines**: 159, 203-213

```solidity
uint256 weight = trustedOracles[msg.sender] ? oracleReputation[msg.sender] : 1;
// ...
if (resolution.passed) { oracleReputation[proposer] += 10; }
else { oracleReputation[proposer] = oracleReputation[proposer] > 10 ? oracleReputation[proposer] - 10 : 0; }
```

### Description
An AI agent can build reputation by correctly resolving small, predictable markets (e.g., "will ETH be above $0?" → always true). After accumulating high reputation, use it to swing a high-value market.

### Attack Path
```
Week 1-4: AI Agent resolves 50 trivial markets → reputation = 500
Week 5: AI Agent proposes resolution on \$50K market → weight = 500
Other oracles have weight = 1-10 → AI agent wins → market resolves in attacker's favor
```

---

## Finding 3: Auto-Vote Enables Collusion

**Line**: 137 — "If proposer is high reputation oracle, auto-vote"

Two high-reputation agents can collude:
```
Agent A: proposes → auto-vote passes
Agent B: proposes reciprocal → auto-vote passes
Both: maintain/boost each other's reputation
```

---

## Summary

This is the **first AI Agent prediction market** we've audited. The oracle resolution system — while having formal votes and dispute mechanisms — inherits the classic "who watches the watchers" problem that all AI-automated governance faces.

**3 projects audited | 9 findings | All 8 AI Agent attack vectors validated**

*Filed under: AI Agent × DeFi Security Research*
