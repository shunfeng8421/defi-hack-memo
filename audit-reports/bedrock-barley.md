# 2 More Exploit Findings

## 1. Bedrock_DeFi $1.7M — Mint Function Exploit
- **Loss**: ~$1.7M USD
- **Date**: September 2024
- **Root**: `mint()` function (L2417-2420) lacked proper validation — attacker minted unlimited tokens
- **Pattern**: #17 Mint/Burn Asymmetry

## 2. BarleyFinance $130K — wBARL Flash Loan
- **Loss**: ~$130K
- **Date**: January 2024
- **Root**: wBARL token's `flash()` function allowed flash-loaned tokens to manipulate protocol state
- **Pattern**: #1 Flash Loan + Oracle

---

**Running total: 25 findings | ~$79.4M**
