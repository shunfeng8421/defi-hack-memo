# Agent Prediction Markets — Composite Final Report

| Contract | Lines | Score | Key Finding |
|------|--:|:--:|------|
| OracleResolver | 369 | 2/10 | adminResolve backdoor + owner-oracle collusion |
| BettingEngine | 453 | 3.5/10 | Assembly garbage-read makes payout unreliable |
| AgentRegistry | 480 | 7/10 | Clean — proper access control |
| TreasuryManager | 309 | 7/10 | Clean — standard patterns |
| MarketFactory | 417 | 6/10 | Factory pattern, standard |
| **Overall** | **2,028** | **3.5/10** | Two independent catastrophic vectors |

## Root Cause Analysis

The protocol has not one, but TWO ways for the owner to steal all funds:

1. **Oracle path**: `adminResolve()` → mark any outcome as winner → claim winnings
2. **Assembly path**: `mload(add(data, 320))` reads garbage → any bettor can "win" by being lucky

The oracle backdoor is a design choice. The assembly bug is an implementation error. Together, they make the protocol's prediction market functionality indistinguishable from a coin flip that the owner controls.

## What Makes This Audit Different

Unlike all other protocols we've audited (Sunna 9.8, Kleidi 9.5, Cherum 9.0), this protocol achieves TWO critical findings through completely independent attack vectors. This is extremely rare — most protocols either have zero criticals or one well-understood trade-off. Having two independent catastrophes suggests the code was never seriously reviewed for security.

## Lesson

Assembly should never be used for ABI decoding. The Solidity compiler solved this problem years ago. When you see `assembly { mload(...) }` in a production contract, you're looking at a bug that hasn't been discovered yet.
