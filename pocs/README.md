# Foundry PoC Portfolio — 6 DeFi Security Findings

All PoCs are self-contained Foundry fork tests. Each demonstrates a real vulnerability discovered during competitive security audits.

## PoC List

| # | Project | Finding | Pattern | Severity |
|:--:|------|------|:--:|:--:|
| 1 | ThunderLoan | Flash loan oracle manipulation via TSwap spot price | #1 Flash Loan | 🔴 CRITICAL |
| 2 | BossBridge | ECDSA signature replay (no nonce/chainId) | #17 Sig Replay | 🔴 CRITICAL |
| 3 | vault-core | ERC-4626 first-depositor inflation attack | #5 Inflation | 🟠 HIGH |
| 4 | PresidentElector | EIP-712 TYPEHASH: uint256[] vs address[] | EIP-712 Typo | 🟠 HIGH |
| 5 | SnowmanAirdrop | EIP-712 TYPEHASH: "addres" spelling error | EIP-712 Typo | 🟠 HIGH |
| 6 | Olympus | BondingCalculator spot price manipulation | #1 Flash Loan | 🔴 CRITICAL |

## Quick Start

```bash
# All PoCs are standalone — no external dependencies needed
forge test --match-path "**/pocs/**" -vvv
```

## Author

**Shiqiang Chen** — Independent Security Researcher  
GitHub: [shunfeng8421](https://github.com/shunfeng8421)  
Repository: [defi-hack-memo](https://github.com/shunfeng8421/defi-hack-memo)
