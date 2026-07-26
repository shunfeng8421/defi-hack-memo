# Appendix A: Complete Pattern Reference (100 Patterns)

## Flash Loan Patterns (#1-3)
| ID | Name | Severity | Real Case |
|:--:|------|:--:|------|
| 1 | Spot Price Oracle | CRITICAL | PancakeBunny $120M |
| 2 | CEI Violation (Reentrancy) | CRITICAL | DAO $60M |
| 3 | Flash + Reentrancy Combo | CRITICAL | CREAM $130M |

## Oracle Manipulation (#4-8)
| 4 | Spot Oracle via getReserves | CRITICAL | Harvest $34M |
| 5 | Chainlink Stale Price | HIGH | Venus $11M |
| 6 | TWAP Multi-Block | HIGH | — |
| 7 | Self-Reported Oracle | CRITICAL | — |
| 8 | ERC-4626 Vault Inflation | CRITICAL | — |

## Access Control (#9-12)
| 9 | Missing Access Control | HIGH | PolyNetwork $610M |
| 10 | Admin Key Privilege | HIGH | Ronin $625M |
| 11 | Unprotected selfdestruct | CRITICAL | — |
| 12 | Delegatecall to User | CRITICAL | Parity $150M |

## Token Economics (#13-16)
| 13 | Fee-on-Transfer | HIGH | — |
| 14 | Rebase Token | HIGH | — |
| 15 | Mint/Burn Asymmetry | MEDIUM | — |
| 16 | Permit Without Nonce | MEDIUM | — |

## Cross-Chain (#17-20)
| 17 | Cross-Chain Replay | CRITICAL | — |
| 18 | Bridge Arbitrary Call | CRITICAL | — |
| 19 | Validator Collusion | CRITICAL | Ronin $625M |
| 20 | Unverified Message Format | CRITICAL | Nomad $152M |

## Reentrancy (#21-24)
| 21 | Classic Reentrancy | CRITICAL | DAO $60M |
| 22 | ERC-777 Callback | HIGH | — |
| 23 | Cross-Function | HIGH | — |
| 24 | Read-Only Reentrancy | MEDIUM | — |

## Initialization (#25-28)
| 25 | Unprotected Initializer | HIGH | Uranium $50M |
| 26 | Storage Collision | CRITICAL | — |
| 27 | Beacon Proxy Swap | HIGH | — |
| 28 | CREATE2 Re-deploy | HIGH | — |

## Precision & Gas (#29-33)
| 29 | Division Before Multiply | MEDIUM | — |
| 30 | Unsafe Downcast | MEDIUM | — |
| 31 | Unit Confusion (wad/bps) | HIGH | Futureswap $394K |
| 32 | Unbounded Loop | MEDIUM | — |
| 33 | Hardcoded Gas (2300) | LOW | — |

## Governance (#34-37)
| 34 | Flash Loan Governance | CRITICAL | Beanstalk $182M |
| 35 | Timelock Front-Run | HIGH | — |
| 36 | Multi-Sig Social Engineering | HIGH | Ronin $625M |
| 37 | Hidden Owner Backdoor | CRITICAL | — |

## MEV & Front-Running (#38-42)
| 38 | Classic Sandwich Attack | HIGH | — |
| 39 | Just-In-Time Liquidity | HIGH | — |
| 40 | Multi-Block MEV | MEDIUM | — |
| 41 | MEV Bot Counter-Attack | HIGH | makina $5.1M |
| 42 | Slippage Control Exploitation | HIGH | xWin |

## Lending & Liquidation (#43-46)
| 43 | Bad Debt Accumulation | HIGH | RadiantCapital $4.5M |
| 44 | Liquidation Front-Running | HIGH | — |
| 45 | Non-Liquidatable Collateral | HIGH | — |
| 46 | Health Factor Rounding | MEDIUM | Hundred $7.4M |

## DEX Concentrated Liquidity (#47-49)
| 47 | JIT Liquidity Extraction | HIGH | — |
| 48 | Tick Boundary Manipulation | HIGH | — |
| 49 | Fee Tier Arbitrage | MEDIUM | — |

## DePIN Physical Layer (#50-53)
| 50 | Location Spoofing | HIGH | Helium |
| 51 | Storage Proof Forgery | CRITICAL | Filecoin |
| 52 | Sensor Data Manipulation | HIGH | WeatherXM |
| 53 | Bandwidth Inflation | MEDIUM | — |

## ZK Circuit (#54-57)
| 54 | Unconstrained Signal | CRITICAL | Tornado Cash |
| 55 | Overflow Wrapping | HIGH | — |
| 56 | Trusted Setup Compromise | CRITICAL | — |
| 57 | Recursive Proof Amplification | HIGH | — |

## RWA Tokenization (#58-60)
| 58 | Double-Minting (Fractional) | CRITICAL | — |
| 59 | Custody Failure | CRITICAL | Celsius |
| 60 | Redemption Failure | CRITICAL | — |

## GameFi Economics (#61-63)
| 61 | Tokenomic Death Spiral | CRITICAL | Axie Infinity |
| 62 | On-Chain RNG Manipulation | HIGH | — |
| 63 | Bot Farming | HIGH | — |

## AI Agent Security (#64-66)
| 64 | Prompt Injection via Tool | CRITICAL | CherryStudio |
| 65 | AI Output Injection | HIGH | — |
| 66 | Model Reward Hacking | MEDIUM | — |

## Slippage & Price Impact (#67-69)
| 67 | Unbounded Price Impact | HIGH | xWin |
| 68 | Stale State Variable | MEDIUM | — |
| 69 | Array Duplicate Check | MEDIUM | — |

## 🆕 L2 Optimistic Rollup (#70-73)
| 70 | Challenge Period Exhaustion | LOW | — |
| 71 | Fraud Proof Bond Arbitrage | MEDIUM | — |
| 72 | Sequencer Censorship | LOW | — |
| 73 | Withdrawal Delay Divergence | DESIGN | — |

## 🆕 Restaking / EigenLayer (#74-79)
| 74 | Slashing Condition Ambiguity | HIGH | — |
| 75 | AVS Malicious Slashing | CRITICAL | — |
| 76 | Delegation Concentration | HIGH | — |
| 77 | Withdrawal Queue Front-Run | MEDIUM | — |
| 78 | Cross-AVS Cascade | HIGH | — |
| 79 | LSD Derivative Amplification | HIGH | Lido |

## 🆕 Intent Architecture (#80-85)
| 80 | Solver Collusion | HIGH | CowSwap |
| 81 | Solver Front-Running | HIGH | — |
| 82 | Reference Price Manipulation | HIGH | — |
| 83 | Solver Default (Credit Risk) | HIGH | — |
| 84 | Intent Cross-Chain Replay | HIGH | — |
| 85 | Intent Ambiguity Exploit | MEDIUM | — |

## 🆕 MPC Wallet (#86-89)
| 86 | Provider Concentration | HIGH | Fireblocks |
| 87 | MPC Protocol Flaw | CRITICAL | — |
| 88 | Side-Channel via Timing | HIGH | — |
| 89 | Social Recovery Bypass | HIGH | Ronin $625M |

## 🆕 ERC-4626 Vault (#90-93)
| 90 | Inflation Attack | CRITICAL | — |
| 91 | maxDeposit/maxMint Rounding | MEDIUM | — |
| 92 | previewRedeem vs redeem | HIGH | — |
| 93 | totalAssets Donation | HIGH | — |

## 🆕 Cross-Chain Intent (#94-96)
| 94 | Relayer Front-Running | HIGH | Across |
| 95 | Settlement Dispute (Reorg) | HIGH | — |
| 96 | Relayer Collusion | MEDIUM | — |

## 🆕 Final Four (#97-100)
| 97 | ERC-4337 EntryPoint Griefing | MEDIUM | — |
| 98 | MEV-Boost Relay Censorship | HIGH | — |
| 99 | SUAVE TEE Side-Channel | HIGH | — |
| 100 | LSD Depeg Cascade | CRITICAL | Lido/ETH |

---

**100 Patterns · 20 Domains · 824 Exploit Reports · $1.05B Verifiable Losses**
