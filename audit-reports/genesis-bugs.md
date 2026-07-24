# DeFi Genesis Bugs — 2 More

## 1. BEC Token (2018) — Integer Overflow
- **Loss**: Token value collapsed
- **Date**: April 2018
- **Pattern**: Integer overflow/underflow
- **Root**: `batchTransfer(address[],uint256)` — `amount * cnt` overflow → unlimited tokens

## 2. Parity Wallet Freeze (2017) — `initWallet` Delegatecall
- **Loss**: 513,774 ETH frozen (~$150M+)
- **Date**: November 2017
- **Pattern**: #41 Delegatecall to unprotected init function
- **Root**: `initWallet()` could be called by anyone → `kill()` set owner=0 → all funds frozen

---

**Total: 63 findings | ~$1B+ | 2017-2026 十年**
