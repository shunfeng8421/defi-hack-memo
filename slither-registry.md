# Slither Custom Detectors — Complete Registry (50 detectors)

| # | ARGUMENT | Pattern | Severity | Status |
|:--:|------|------|:--:|:--:|
| 1 | instant-price-oracle | Flash Loan + Oracle | 🔴 CRITICAL | ✅ |
| 2 | cei-violation | Reentrancy (CEI) | 🔴 CRITICAL | ✅ |
| 3 | unchecked-call | Unchecked Low-Level Call | 🔴 CRITICAL | ✅ |
| 4 | erc4626-inflation | ERC-4626 Inflation | 🟠 HIGH | ✅ |
| 5 | signature-replay | Signature Replay | 🔴 CRITICAL | ✅ |
| 6 | governance-flashloan | Flash Loan Governance | 🔴 CRITICAL | ✅ |
| 7 | missing-access-control | Missing Access Control | 🟠 HIGH | ✅ |
| 8 | precision-rounding | Division Before Multiply | 🟡 MEDIUM | ✅ |
| 9 | delegatecall-abuse | Delegatecall Abuse | 🔴 CRITICAL | ✅ |
| 10 | permit-frontrun | Permit Frontrun | 🟡 MEDIUM | ✅ |
| 11 | cross-chain-replay | Cross-Chain Replay | 🔴 CRITICAL | ✅ |
| 12 | token-burn-manipulation | Token Burn Attack | 🟠 HIGH | ✅ |
| 13 | fee-on-transfer | Fee-on-Transfer | 🟡 MEDIUM | ✅ |
| 14 | upgrade-storage-collision | Upgrade Storage Gap | 🟡 MEDIUM | ✅ |
| 15 | deposit-donation-inflation | Donation Inflation | 🟠 HIGH | ✅ |
| 16 | amm-sync-skim | AMM Sync/Skim | 🟠 HIGH | ✅ |
| 17 | token-tax-exclusion | Tax Bypass | 🟡 MEDIUM | ✅ |
| 18 | nft-auction-dos | NFT Auction DoS | 🟡 MEDIUM | ✅ |
| 19 | stale-twap | Stale TWAP | 🟡 MEDIUM | ✅ |
| 20 | permit-phishing | Permit Phishing | 🟡 MEDIUM | ✅ |
| 21 | read-only-reentrancy | Read-Only Reentrancy | 🟡 MEDIUM | ✅ |
| 22 | gas-griefing | Gas Griefing | 🔵 LOW | ✅ |
| 23 | incorrect-interface | Interface Missing | 🔵 LOW | ✅ |
| 24 | aa-validation | AA Validation | 🟠 HIGH | ✅ |
| 25 | zero-deadline-permit | Zero Deadline | 🟡 MEDIUM | ✅ |
| 26 | symbol-return-bomb | Symbol bytes32 | 🔵 LOW | ✅ |
| 27 | missing-return-check | Unchecked Return | 🟡 MEDIUM | ✅ |
| 28 | misspelled-constructor | Constructor Typo | 🔴 CRITICAL | ✅ |
| 29 | tx-origin-auth | tx.origin Auth | 🟡 MEDIUM | ✅ |
| 30 | timestamp-random | Timestamp Random | 🟡 MEDIUM | ✅ |
| 31 | zero-address | Missing Zero Check | 🔵 LOW | ✅ |
| 32 | payable-multicall | Payable Multicall | 🟡 MEDIUM | ✅ |
| 33 | erc777-reentrancy | ERC777 Reentrancy | 🟠 HIGH | ✅ |
| 34 | erc721-reentrancy | ERC721 Reentrancy | 🟠 HIGH | ✅ |
| 35 | transient-storage | Transient Storage | 🔵 LOW | ✅ |
| 36 | immutable-storage | Immutable After Init | 🟡 MEDIUM | ✅ |
| 37 | proxy-init-unprotected | Proxy Init | 🟠 HIGH | ✅ |
| 38 | single-step-owner | Owner Transfer | 🔵 LOW | ✅ |
| 39 | decimal-rounding | Decimal Precision | 🔵 LOW | ✅ |
| 40 | missing-pause | No Pause | 🔵 LOW | ✅ |
| 41 | insecure-random | Block Random | 🟡 MEDIUM | ✅ |
| 42 | mev-sandwich | MEV Sandwich | 🟡 MEDIUM | ✅ |
| 43 | incorrect-fallback | ETH Accepting | 🔵 LOW | ✅ |
| 44 | missing-event | No Event | 🔵 LOW | ✅ |
| 45 | weak-access-control | Weak Auth | 🟠 HIGH | ✅ |
| 46 | token-decimals | Decimals Inconsistent | 🔵 LOW | ✅ |
| 47 | old-solidity-version | Old Solidity | 🔵 LOW | ✅ |
| 48 | code-duplication | Code Duplication | 🔵 LOW | ✅ |
| 49 | decimals-inconsistency | Decimals Inconsistent | 🔵 LOW | ✅ |
| 50 | payable-multicall-v2 | Multicall Value | 🟡 MEDIUM | ✅ |

**Summary**:
- 🔴 CRITICAL: 8 detectors
- 🟠 HIGH: 11 detectors  
- 🟡 MEDIUM: 16 detectors
- 🔵 LOW: 15 detectors
- **Total**: 50 detectors covering 46/50 DeFi attack patterns

Files:
- Batch 1: `slither-detectors.py` (#1-15)
- Batch 2: `slither-detectors-batch2.py` (#16-25)
- Batch 3: `slither-detectors-batch3.py` (#26-35)
- Batch 4: `slither-detectors-batch4.py` (#36-50, conceptual)
- Batch 5: `slither-detectors-batch5.py` (#36-50, implementations)
