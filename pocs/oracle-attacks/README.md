# Oracle Manipulation Lab — 10 Attack Vectors

| # | Name | Oracle Type | Severity | Real Case |
|:--:|------|------|:--:|------|
| 1 | Spot Price | Uniswap V2 getReserves() | 🔴 | PancakeBunny $120M |
| 2 | TWAP Multi-Block | Uniswap V2 cumulative | 🟠 | — |
| 3 | Stale Price | Chainlink | 🔴 | Venus $11M |
| 4 | Self-Reported | Custom | 🔴 | CREAM $130M |
| 5 | LP Token Collateral | AMM pool value | 🔴 | Warp Finance $7.8M |
| 6 | Curve Virtual Price | Curve | 🟠 | — |
| 7 | Balancer Spot | Balancer | 🟠 | — |
| 8 | Multi-Hop | Path-dependent | 🟡 | — |
| 9 | Admin Updatable | Centralized | 🔴 | — |
| 10 | Delayed Oracle | Time-gap | 🟠 | — |

**Run**: `pocs/oracle-attacks/OracleAttackLab.sol`
**Patterns**: #1-5 in 58-pattern scanner
