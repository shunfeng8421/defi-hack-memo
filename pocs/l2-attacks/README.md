# Optimistic Rollup Security — 6 Fraud Proof Attack Vectors

## Why L2 Security Matters

Arbitrum ($18B TVL), Optimism ($8B), and Base ($4B) collectively secure more value than most L1 chains. Every protocol deployed on these chains inherits the security model of the underlying rollup. A bug in the fraud proof mechanism affects every protocol on the chain.

## The 6 Attack Vectors

| # | Attack | Real Risk | Pattern # |
|:--:|------|:--:|:--:|
| 1 | Challenge Period Exhaustion (L1 congestion) | Low | #70 |
| 2 | Bond Arbitrage (sub-scale bond) | Medium | #71 |
| 3 | Sequencer Censorship (pre-EIP-4844) | Low (fixed) | #72 |
| 4 | Fraud Proof Verification Bug | Unknown | — |
| 5 | Multi-Round Griefing | Low (BOLD protocol) | — |
| 6 | Withdrawal Delay Divergence | Design constraint | #73 |

## Key Insight

The most dangerous L2 attack is not a single vulnerability — it's the interaction between L1 and L2 security models. A protocol that is secure on L1 (e.g., Chainlink oracle with 1-hour heartbeat) may be insecure on L2 (where state updates take 7 days for finality).

## Our Pattern Map

This lab adds 3 new patterns (#70-73) to our taxonomy, bringing the total to 69 confirmed patterns.
