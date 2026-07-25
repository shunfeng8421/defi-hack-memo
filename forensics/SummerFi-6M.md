# On-Chain Forensics: SummerFi $6M
## NAV Manipulation — The Post-Oracle Era

**Date**: July 2026  
**Amount**: $6M  
**Protocol**: SummerFi — leveraged yield protocol  
**Root Cause**: FleetCommander NAV calculated from manipulable DEX price, not oracle

---

## Attack Flow

```
┌───────────────────────────────────────────────────┐
│ SummerFi FleetCommander Architecture                │
│                                                    │
│ NAV = Σ(asset_balance_i × price_i)                 │
│ NAV determines:                                     │
│   - Max borrow amount                               │
│   - Liquidation threshold                            │
│   - Deposit/withdraw limits                          │
├────────────────────────────────────────────────────┤
│ Step 1: Flash loan large amount of asset A          │
│ Swap asset A → asset B on DEX                       │
│ Price of B relative to A spikes                      │
├────────────────────────────────────────────────────┤
│ Step 2: Deposit B into FleetCommander               │
│ FleetCommander reads NAV using DEX spot price       │
│ NAV inflated → huge borrow capacity                 │
├────────────────────────────────────────────────────┤
│ Step 3: Borrow maximum against inflated NAV         │
│ Actual collateral: $1M                               │
│ Apparent collateral: $20M                            │
│ Borrowed: $7M                                        │
├────────────────────────────────────────────────────┤
│ Step 4: Repay flash loan, keep 6M profit            │
│ Protocol left with $1M collateral, $7M bad debt     │
└────────────────────────────────────────────────────┘
```

## The Post-Oracle Era

SummerFi represents a new class of DeFi attack: **not the oracle is manipulated, but NAV calculation is manipulated using DEX prices.**

The protocol didn't use Chainlink or any oracle. It used DEX spot prices directly. This was intentionally "oracle-free" — a design choice that became the attack vector.

## The Pattern

This is what the handbook calls "post-oracle era" attacks:
- Protocols move away from oracle dependency
- But replace it with DEX spot price dependency
- DEX spot prices are MORE manipulable than Chainlink oracles
- Result: the attack surface moves, but doesn't shrink

## Fix

```solidity
// NEVER: price = pool.getReserves()
// ALWAYS: price = oracle.getTWAP(30 minutes)
function getNAV() public view returns (uint256) {
    uint256 total;
    for (uint i = 0; i < assets.length; i++) {
        total += balances[i] * twapOracle.getPrice(assets[i]);
    }
    return total;
}
```

## Pattern

Pattern #43: NAV Manipulation via DEX spot price — Protocol replaces centralized oracle with decentralized DEX price, creating a more exploitable attack surface.
