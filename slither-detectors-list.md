# Slither Custom Detectors Library — 15 Rules
# Covers DeFi 50-Pattern Classification
# Author: Shiqiang Chen — July 2026

## Implemented Detectors

| # | Detector | Pattern | Severity | Source |
|:--:|------|:--:|:--:|------|
| 1 | instant-price-oracle | #1 | HIGH | TWAP detector |
| 2 | unchecked-transfer | #2 | MEDIUM | slither built-in+ |
| 3 | signature-replay | #27 | HIGH | BossBridge/PolyNet |
| 4 | erc4626-inflation | #5 | HIGH | vault-core |

## New Detectors to Implement

| # | Detector | Pattern | Target |
|:--:|------|:--:|------|
| 5 | cei-violation | #2 | external call before state update |
| 6 | governance-flashloan | #11 | flash loan + governance token |
| 7 | missing-access-control | #8 | public function without auth |
| 8 | precision-rounding-loss | #46 | mul before div, truncation |
| 9 | delegatecall-abuse | #13 | delegatecall to untrusted |
| 10 | permit-frontrun | #15 | permit without deadline |
| 11 | cross-chain-replay | #34 | no chainId in bridge msg |
| 12 | token-burn-manipulation | #25 | transfer burn affecting pair |
| 13 | fee-on-transfer-mishandling | #39 | balance check without fee |
| 14 | upgrade-storage-collision | #13 | missing __gap in upgradeable |
| 15 | deposit-donation-inflation | #5 | no minDeposit protection |
