# PropFund — AI Agent Prop Trading Fund Audit

**Auditor**: Shiqiang Chen | **Date**: July 18, 2026  
**Project**: PropFund.eth | **Contract**: PropFund.sol (1,600 lines)

## Executive Summary

The most architecturally mature AI Agent × DeFi protocol yet. Pyth oracle eliminates MEV. Per-trade caps limit AI agent authority. But permissionless forceClose creates a race condition.

| # | Finding | Severity | AI Attack Vector |
|:--:|------|:--:|------|
| 1 | Permissionless forceClose — race with agent | 🟡 MEDIUM | Vector #5: Timing Window |
| 2 | eval→fund transition is AI-gamable | 🟡 MEDIUM | Vector #7: Context Poisoning |
| 3 | Pyth oracle trust (positive) | ✅ NONE | Designed against Vector #3 |

## Finding 1: Permissionless forceClose Enables Race with Agent

**Lines**: 1283-1296

```solidity
function forceClose(address trader) external nonReentrant {
    // Permissionless: close position older than 14 days
    if (block.number < uint256(pos.openBlock) + MAX_POSITION_BLOCKS) revert PositionNotExpired();
```

### Attack
1. AI Agent opens position → position ages 14 days
2. Agent detects position about to expire → sends close tx
3. Attacker sees agent's tx in mempool → front-runs with forceClose
4. Attacker earns the close fee/bounty → agent earns nothing

### AI Agent Impact
The AI agent has no way to guarantee it closes its own position. A searcher can always front-run close older positions.

### Fix
Add a 1-block priority window where only the trader/controller can close.

---

## Finding 2: Eval Phase Is AI-Gamable

**Lines**: EVAL_PROFIT_BPS threshold

An AI agent can be programmed to:
1. Pass eval by making trivial high-probability trades
2. Once funded, crank up risk since losses are absorbed by the pool
3. Collect profit share while pool bears the downside

This is **asymmetric risk**: the agent has upside but limited downside (deposit is small relative to pool capital). The eval mechanism tests for profit but not for risk-adjusted skill.

---

## Finding 3: Pyth Oracle Design (Positive)

**Line 29**: "Every wired feed is locked at expo == -8. No DEX, no AMM, no MEV surface."

This is the **correct** approach for AI Agent trading. Pyth's oracle model prevents Vector #3 (Oracle Poisoning) entirely because:
- No on-chain pool to manipulate
- Price feeds come from off-chain providers
- Expo is standardized to prevent precision attacks

---

## Assessment

PropFund is the most security-conscious AI Agent × DeFi protocol we've audited. The Pyth oracle + per-trade caps + delegation expiry shows mature thinking about the AI agent attack surface. The remaining issues are moderate and related to timing/fairness rather than fund loss.

---

**AI Agent × DeFi Audit Series**: 4 projects | 12 findings | 6/8 attack vectors validated
