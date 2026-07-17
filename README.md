# 🛡️ DeFi Security Scanner

[![Marketplace](https://img.shields.io/badge/GitHub%20Marketplace-DeFi%20Scanner-red)](https://github.com/marketplace/actions/defi-security-scanner)
[![50 Patterns](https://img.shields.io/badge/Patterns-50-blue)](https://github.com/shunfeng8421/defi-hack-memo)

**Scan Solidity code against 50 DeFi attack patterns backed by 824 real-world incidents.**

---

## Quick Start

Add to `.github/workflows/scan.yml`:

```yaml
name: DeFi Audit
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: shunfeng8421/defi-hack-memo@master
```

That's it. Every push scans all `*.sol` files automatically.

---

## What It Detects

| Category | Patterns | Examples |
|------|:--:|------|
| Flash Loan | 8 | Price oracle, governance capture, reentrancy |
| Access Control | 8 | Missing auth, unprotected init, upgrade collision |
| Authorization | 8 | Signature replay, cross-chain replay, EIP-712 typo |
| Economic Attacks | 8 | ERC-4626 inflation, token burn, fee manipulation |
| Precision | 7 | Integer overflow, division before multiply, rounding |
| Oracle | 6 | Stale oracle, TWAP manipulation, L2 sequencer |
| Protocol Logic | 5 | Backdoors, accounting bugs, batch DoS |

**Coverage**: 97.6% of 824 known DeFi exploits.

---

## Output

```
📄 Vault.sol
  🔴 [05] ERC-4626 Inflation Attack (CRITICAL)
      First depositor can donate assets to inflate share price
      Lines: 42-67
      Fix: Mint dead shares on initialization

📄 Bridge.sol
  🔴 [17] Signature Replay (CRITICAL)
      Cross-chain message signed without nonce or chainId
      Lines: 112-130
      Fix: Include nonces[signer]++ and block.chainid
```

---

## Advanced

```yaml
- uses: shunfeng8421/defi-hack-memo@master
  with:
    path: 'contracts/'           # Scan specific directory
    fail_on_critical: 'true'    # Block merge if CRITICAL found
```

---

## Backed By

- **824 real DeFi incidents** analyzed (2017-2026)
- **50 custom Slither detectors**
- **6 peer-reviewed papers** (Zenodo DOI indexed)
- **CodeHawks BattleChain** competition validated

---

## Author

**Shiqiang Chen**  
Independent Security Researcher  
[GitHub](https://github.com/shunfeng8421) · [Email](shunfeng8421@163.com)
