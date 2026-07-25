# On-Chain Forensics Report
## Euler Finance $197M — Transaction-Level Reconstruction

**Date**: March 13, 2023  
**Tx**: 0xc310a0affe2169d1f6feec1c63dbc7f7c62a887fa48795d327d4d2da2d6b111d  
**Attacker**: 0xebc291... (1,004-day dormant wallet)  
**Root Cause**: donateToReserves() allowed manipulation of exchange rate between eDAI and dDAI

---

## Attack Flow

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: Flash Loan                                      │
│ Aave v2 + Balancer → 30M DAI                            │
│ Cost: ~$3,000 gas                                       │
├─────────────────────────────────────────────────────────┤
│ Step 2: Deploy Attack Contracts                         │
│ Contract A: "Violator" — deposits & borrows             │
│ Contract B: "Liquidator" — liquidates Violator          │
├─────────────────────────────────────────────────────────┤
│ Step 3: Deposit to Euler                                │
│ Violator: deposit 20M DAI → receive 19.5M eDAI          │
│                                                         │
│ Euler tracks: eDAI:DAI ratio = 19.5M:20M = 0.975        │
├─────────────────────────────────────────────────────────┤
│ Step 4: Exploit mint() — Borrow 10x                     │
│ Violator: mint() → receive 195.6M eDAI + 200M dDAI     │
│                                                         │
│ KEY BUG: mint() allows borrowing 10x collateral         │
│ WITHOUT proper health factor check                      │
├─────────────────────────────────────────────────────────┤
│ Step 5: Partial Repay                                   │
│ Repay 10M DAI → burn 10M dDAI                           │
│ Debt reduced: 200M → 190M dDAI                           │
├─────────────────────────────────────────────────────────┤
│ Step 6: Second mint() — Compound                        │
│ mint() again → +195.6M eDAI + 200M dDAI                 │
│ Total debt: 390M dDAI                                    │
├─────────────────────────────────────────────────────────┤
│ Step 7: Manipulate Exchange Rate                        │
│ donateToReserves 100M eDAI → eDAI:DAI ratio spikes       │
│                                                         │
│ THIS IS THE ROOT CAUSE:                                 │
│ eDAI supply inflated → exchange rate distorted           │
│ dDAI appears undervalued → triggers liquidation          │
├─────────────────────────────────────────────────────────┤
│ Step 8: Self-Liquidation                                 │
│ Liquidator: liquidate(Violator)                          │
│ Receives: 310M eDAI + assumes 259M dDAI debt            │
│                                                         │
│ The liquidation was PROFITABLE because                   │
│ donateToReserves made eDAI worth more than dDAI          │
├─────────────────────────────────────────────────────────┤
│ Step 9: Withdraw                                         │
│ withdraw 38.9M DAI from Euler                            │
│ 38.9M - 30M (flash loan repayment) = 8.9M DAI profit    │
└─────────────────────────────────────────────────────────┘
```

## The Vulnerability Chain

The exploit required FOUR bugs to work together:

1. **mint() unlimited borrow**: Euler's mint function allowed borrowing up to 10x collateral without proper health factor check
2. **donateToReserves() manipulation**: Donating tokens to reserves skewed the eToken/dToken exchange rate
3. **Self-liquidation profitability**: The skewed rate made self-liquidation profitable
4. **Leverage amplification**: Repeating mint→repay→mint allowed 10x→100x leverage

**Single-point fix**: If ANY of these four bugs had been patched, the attack fails.

## Pattern Mapping

This attack combines patterns from the 66-pattern taxonomy:
- Pattern #1: Flash Loan amplification
- Pattern #13: Token economics manipulation (donateToReserves)
- Pattern #38: Bad debt accumulation (mint() without health check)
- Pattern #32: Self-liquidation profitability

## Lessons

1. **Donation functions that affect exchange rates are dangerous.** Any function that changes a token's effective price without changing its collateral value is a manipulation vector.
2. **Borrow limits must be enforced at EVERY entry point.** Euler's mint(), deposit(), and repay() all changed the health factor — but only some of them checked it.
3. **Self-liquidation should never be profitable.** If a user can profit from liquidating their own position, the liquidation mechanism is broken.
