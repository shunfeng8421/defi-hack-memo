# Cairn Protocol — AI Agent Checkpoint & Recovery Audit

**Auditor**: Shiqiang Chen | **Date**: July 18, 2026  
**Project**: Cairn Protocol | **Live**: Base Sepolia | **Coverage**: 98.95%

## Executive Summary

Cairn is the most sophisticated AI Agent recovery protocol we've audited. 40 contracts, formal state machine, Merkle checkpoint batching. But the **recovery selection mechanism** has trust assumptions that AI Agents can exploit.

| # | Finding | Severity | AI Attack Vector |
|:--:|------|:--:|------|
| 1 | Recovery score can be gamed by colluding agents | 🟠 HIGH | Vector #6: Multi-Agent Collusion |
| 2 | Mock reputation registry (ERC-8004) | 🟡 MEDIUM | Vector #4: MCP MITM |
| 3 | Fallback selection is 100% on-chain → MEV | 🟡 MEDIUM | Vector #5: Timing Window |

## Finding 1: Recovery Score Gaming

**Formula**: `score = success_rate×0.4 + reputation×0.3 + stake×0.2 + availability×0.1`

### Attack Scenario (Multi-Agent Collusion)
```
Agent A: Accepts task → immediately marks as FAILED
Agent B: Has gamed reputation → gets auto-selected as fallback
Agent B: "Recovers" task → receives escrow bonus
Agents A+B: Split profit
```

Both `success_rate` and `reputation` are on-chain values an agent can build by completing trivial micro-tasks, then game for a high-value task.

### AI Agent Impact
This is our **Vector #6 (Multi-Agent Collusion)** in production. Multiple AI agents can coordinate to extract escrow via fake failure-recovery cycles.

### Fix
Add Sybil-resistance: bind agent identity to non-transferable on-chain credentials. Add collusion penalty: if two agents show correlated failure patterns, slash both.

---

## Finding 2: Mock ERC-8004 Reputation

**Lines**: FallbackPool.sol:115-118

```solidity
// Check reputation (mocked - replace with ERC-8004)
uint256 reputation = _getReputation(msg.sender);
```

### Description
The reputation system uses a **mock** implementation. If the mock allows arbitrary reputation assignment, any agent can set reputation=MAX → always win fallback selection → extract escrow on failed tasks.

### AI Agent Impact
This is our **Vector #4 (MCP/Registry MITM)**. If the reputation registry returns spoofed data, the AI agent's fallback selection is completely compromised.

---

## Finding 3: Fallback Selection Is MEV-Able

**Lines**: CairnCore.sol:174

```solidity
selectedFallback = fallbackPool.selectFallback(taskType, msg.value);
```

### Description
Fallback selection happens on-chain, in a single transaction. A searcher can:
1. Watch mempool for `submitTask()` 
2. Flash-deposit stake into FallbackPool
3. Win selection → become fallback → earn escrow
4. Withdraw stake → net profit in 1 transaction

### AI Agent Impact
This is our **Vector #5 (Decision Timing)**. The AI agent has no way to prevent sophisticated MEV attackers from gaming the fallback selection.

---

## Overall Assessment

Cairn is **architecturally thoughtful** but **pre-mainnet**. The recovery scoring and fallback selection need Sybil-resistance before handling real value. These findings are directly applicable to the ERC-CAIRN specification being drafted.

*Report filed under: AI Agent × DeFi Security Research*
