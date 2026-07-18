# 3 More Live Exploit Findings

## 1. AlkemiEarn $120K — Flash Loan + Withdraw Logic

- **Loss**: 43.45 ETH (~$120K)
- **Pattern**: #1 Flash Loan + Oracle
- **Root**: Balancer flash loan → borrow WETH → withdraw from Aave aWETH at manipulated price → profit from incorrect withdrawal calculation
- **Detection**: ✅ Scanner Pattern #1

---

## 2. BCE Token $800K — scheduledDestruction Pool Manipulation

- **Loss**: ~$800,000 USDT
- **Pattern**: #16 Token Burn + #7 AMM Reserve
- **Root**: `scheduledDestruction` burns BCE from Pancake pair → `sync()` updates reserves → pair has almost no BCE → attacker sells at massively inflated price
- **Key insight**: The burn mechanism was designed to reduce supply but was exploitable because it burned directly from the LP pair
- **Detection**: ✅ Scanner Pattern #16 + #7

Attack flow:
```
1. Transfer BCE → triggers scheduledDestruction → burns BCE from Pancake pair
2. sync() updates reserves → BCE reserve ≈ 0 → price ≈ ∞
3. Attacker sells BCE → gets huge USDT for almost nothing
4. Profit: 600K+ USDT
```

---

## 3. Unverified Smart Account $85K — Missing Access Control

- **Loss**: 85,730 USDC
- **Pattern**: #12 Missing Access Control
- **Root**: `_ALLOW_ALL_()` returns true → anyone can call `activateAndCall(address, bytes)` → execute arbitrary calldata as the smart account
- **Key insight**: An old BOC (Blockchain Operation Contract) allowed unprivileged EOAs to drain its USDC
- **Detection**: ✅ Scanner Pattern #12

Attack:
```
1. Attacker calls old BOC directly (no access restriction due to _ALLOW_ALL_)
2. Uses activateAndCall() to execute USDC transfer to attacker account
3. $85K USDC drained
```

---

## Summary

Today's hunt: **9 confirmed vulnerabilities | $23.22M total**

| # | Protocol | Loss | Pattern |
|:--:|------|--:|------|
| 1 | WhalebitDeFi | $824K | #1 Oracle |
| 2 | AztecConnect | $2.19M | ZK Bypass |
| 3 | DxSale | $7.3M | #35 Backdoor |
| 4 | VerusBridge | $11.6M | Bridge |
| 5 | futureswap | $394K | #34 Precision |
| 6 | Curve LlamaLend | $240K | #6 Liquidation |
| 7 | AlkemiEarn | $120K | #1 Oracle |
| 8 | BCE Token | $800K | #16 Burn |
| 9 | Unverified Account | $85K | #12 Access |

All 9 patterns matched by our scanner ✅
