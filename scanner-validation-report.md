# Scanner Validation — 10 Known DeFi Attacks

| # | Attack | Loss | Expected Pattern | Detected? |
|:--:|------|--:|------|:--:|
| 1 | bZx | $50M | Flash Loan + Oracle | ✅ |
| 2 | Cream | $130M | Flash Loan + Reentrancy | ✅ |
| 3 | PancakeBunny | $120M | Flash Loan | ✅ |
| 4 | Beanstalk | $182M | Governance | ✅ |
| 5 | Euler | $197M | Lending Liquidation | ✅ |
| 6 | BonqDAO | $88M | Oracle | ✅ |
| 7 | LendfMe | $25M | Reentrancy | ❌ |
| 8 | NomadBridge | $152M | Cross-Chain | ✅ |
| 9 | HedgeyFinance | $48M | Permission | ✅ |
| 10 | OrbitChain | $81M | Signature Replay | ✅ |

**Detection Rate: 90% (9/10)**

LendfMe miss: PoC file is a simplified exploit script without the vulnerable deposit/withdraw pattern — scanner correctly detected other patterns but not the reentrancy specifically.
