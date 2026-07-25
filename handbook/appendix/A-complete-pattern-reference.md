# Appendix A: Complete Pattern Reference (66 Patterns)

## Flash Loan Patterns (#1-3)
| ID | Name | Severity | Real Case | Chapter |
|:--:|------|:--:|------|:--:|
| 1 | Spot Price Oracle | CRITICAL | PancakeBunny $120M | 4 |
| 2 | CEI Violation (Reentrancy) | CRITICAL | DAO $60M | 9 |
| 3 | Flash + Reentrancy Combo | CRITICAL | CREAM $130M | 4 |

## Oracle Manipulation (#4-8)
| ID | Name | Severity | Real Case | Chapter |
|:--:|------|:--:|------|:--:|
| 4 | Spot Oracle via getReserves | CRITICAL | Harvest $34M | 5 |
| 5 | Chainlink Stale Price | HIGH | Venus $11M | 5 |
| 6 | TWAP Multi-Block | HIGH | — | 5 |
| 7 | Self-Reported Oracle | CRITICAL | — | 5 |
| 8 | ERC-4626 Vault Inflation | CRITICAL | — | 5 |

## Access Control (#9-12)
| 9 | Missing Access Control | HIGH | PolyNetwork $610M | 6 |
| 10 | Admin Key Privilege | HIGH | Ronin $625M | 6 |
| 11 | Unprotected selfdestruct | CRITICAL | — | 6 |
| 12 | Delegatecall to User | CRITICAL | Parity $150M | 6 |

## Token Economics (#13-16)
| 13 | Fee-on-Transfer | HIGH | — | 7 |
| 14 | Rebase Token | HIGH | — | 7 |
| 15 | Mint/Burn Asymmetry | MEDIUM | — | 7 |
| 16 | Permit Without Nonce | MEDIUM | — | 7 |

## Cross-Chain (#17-20)
| 17 | Cross-Chain Replay | CRITICAL | — | 8 |
| 18 | Bridge Arbitrary Call | CRITICAL | — | 8 |
| 19 | Validator Collusion | CRITICAL | Ronin $625M | 8 |
| 20 | Unverified Message Format | CRITICAL | Nomad $152M | 8 |

## Reentrancy (#21-24)
| 21 | Classic Reentrancy | CRITICAL | DAO $60M | 9 |
| 22 | ERC-777 Callback | HIGH | — | 9 |
| 23 | Cross-Function | HIGH | — | 9 |
| 24 | Read-Only Reentrancy | MEDIUM | — | 9 |

## Initialization (#25-28)
| 25 | Unprotected Initializer | HIGH | Uranium $50M | 10 |
| 26 | Storage Collision | CRITICAL | — | 10 |
| 27 | Beacon Proxy Swap | HIGH | — | 10 |
| 28 | CREATE2 Re-deploy | HIGH | — | 10 |

## Precision & Gas (#29-33)
| 29 | Division Before Multiply | MEDIUM | — | 11 |
| 30 | Unsafe Downcast | MEDIUM | — | 11 |
| 31 | Unit Confusion (wad/bps) | HIGH | Futureswap $394K | 11 |
| 32 | Unbounded Loop | MEDIUM | — | 11 |
| 33 | Hardcoded Gas (2300) | LOW | — | 11 |

## Governance (#34-37)
| 34 | Flash Loan Governance | CRITICAL | Beanstalk $182M | 12 |
| 35 | Timelock Front-Run | HIGH | — | 12 |
| 36 | Multi-Sig Social Engineering | HIGH | Ronin $625M | 12 |
| 37 | Hidden Owner Backdoor | CRITICAL | — | 12 |

## MEV (#38-42) — Ch14
## Lending (#43-46) — Ch15
## DEX (#47-49) — Ch16
## DePIN (#50-53) — Ch17
## ZK Circuit (#54-57) — Ch18
## RWA (#58-60) — Ch19
## GameFi (#61-63) — Ch20
## AI Agent (#64-66) — Ch21

*(Domain extension patterns detailed in respective chapters)*
