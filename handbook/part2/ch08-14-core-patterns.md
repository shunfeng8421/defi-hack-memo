# Chapters 8-14: Cross-Chain · Reentrancy · Init · Precision · DoS · Gas · Governance

## Chapter 8: Cross-Chain Vulnerabilities (Patterns 19-22)

### Pattern #19: Cross-Chain Replay
**CRITICAL** · Signature without `chainId` → valid on ALL chains. User signs on Ethereum → attacker replays on Polygon, Arbitrum, Base.

### Pattern #20: Bridge Arbitrary Call
**CRITICAL** · Bridge accepts user-supplied calldata → executes on destination. Attacker provides `transfer(all)` instead of `transfer(amount)`.

### Pattern #21: Sandwich Attack
**MEDIUM** · No slippage on swap. Attacker buys before victim, sells after. Victim's slippage = attacker's profit.

### Pattern #22: Unprotected SLOAD after SSTORE
**LOW** · Reading storage after writing → expensive gas → griefing vector.

---

## Chapter 9: Reentrancy & Callbacks (Patterns 23-27)

### Pattern #23: NFT Reentrancy
**HIGH** · NFT transfer triggers `onERC721Received` callback → re-enters contract.

### Pattern #24: NFT Auction DoS
**MEDIUM** · Contract bids then rejects refund → auction permanently stuck.

### Pattern #27: EIP-712 Type Mismatch
**HIGH** · **Real: giddyvaultv3 $1.3M**. TYPEHASH includes `bytes data` but inner struct fields (fromToken, amount) are NOT in the TYPEHASH → signature valid for ANY inner data.

---

## Chapter 10: Initialization & Upgrades (Patterns 28-32)

### Pattern #28: Unprotected Initializer
**HIGH** · **Real: Uranium $50M**. `initialize()` without modifier → anyone calls it on implementation → becomes owner.

### Pattern #29: Selfdestruct Attack
**HIGH** · `selfdestruct` forces ETH into contract → breaks `address(this).balance` accounting.

### Pattern #30: CREATE2 Metamorphic
**MEDIUM** · Deploy → selfdestruct → redeploy different code at SAME address.

### Pattern #31: Rebase Token
**HIGH** · Token balance changes retroactively → protocol has accounting mismatch.

### Pattern #32: Off-Chain Keeper Price
**CRITICAL** · Keeper submits off-chain price → no on-chain validation → keeper is single point of failure.

---

## Chapter 11: Precision & Arithmetic (Patterns 33-36)

### Pattern #34: Precision Loss (wad vs bps)
**CRITICAL** · **Real: futureswap $394K**. `feeRateWad` interpreted as bps → 100x overcharge. Always document units in variable names.

### Pattern #35: Hidden Backdoor
**CRITICAL** · Owner `burn()`/`selfdestruct()` without timelock → single key = total control.

### Pattern #36: TWAP Multi-Block Poisoning
**HIGH** · Control consecutive blocks → cumulative price manipulated → TWAP reads fake value.

---

## Chapter 12: DoS & Griefing (Patterns 37-42)

### Pattern #37: Deposit Lock
**HIGH** · `deposit()` exists but no `withdraw()` → funds permanently locked.

### Pattern #38: Hardcoded Gas (2300)
**LOW** · `.transfer()` only forwards 2300 gas → breaks contract wallets.

### Pattern #40: Phantom Fallback
**MEDIUM** · `fallback()` silently accepts any call → ETH locked.

### Pattern #41: Unsafe Delegatecall
**CRITICAL** · **Real: Parity $150M**. `delegatecall` to user-supplied address → total compromise.

### Pattern #42: ERC-777 Token Callback
**HIGH** · Token callback during transfer → re-enter contract → double-spend.

---

## Chapter 13: Gas & Storage (Patterns 43-48)

### Pattern #44: Unsafe Downcast
**MEDIUM** · `uint128(uint256_max)` silently wraps to 0.

### Pattern #45: Ownership Renounce
**MEDIUM** · `renounceOwnership()` → no admin forever → contract paralyzed.

### Pattern #46: Flash Fee Bypass
**HIGH** · Manipulate token price → fee becomes negligible.

### Pattern #48: Loan Origination Race
**HIGH** · Price checked BEFORE collateral transferred.

---

## Chapter 14: Governance & Admin (Patterns 49-50)

### Pattern #49: Batch Transfer DoS
**MEDIUM** · One failing transfer reverts entire batch.

### Pattern #50: Unbounded Loop
**MEDIUM** · Array grows without limit → exceeds block gas → permanent DoS.

---

## Quick Reference: Patterns 19-50

| # | Pattern | | # | Pattern |
|:--:|------|:--:|:--:|------|
| 19 | Cross-Chain Replay 🔴 | | 35 | Hidden Backdoor 🔴 |
| 20 | Bridge Arbitrary Call 🔴 | | 36 | TWAP Poison 🟠 |
| 27 | EIP-712 Mismatch 🟠 | | 37 | Deposit Lock 🟠 |
| 28 | Unprotected Init 🟠 | | 41 | Unsafe Delegate 🔴 |
| 29 | Selfdestruct 🟠 | | 42 | ERC-777 Callback 🟠 |
| 30 | CREATE2 Morph 🟡 | | 44 | Unsafe Downcast 🟡 |
| 34 | Precision Loss 🔴 | | 50 | Unbounded Loop 🟡 |

---

*Next: Part III — Solana Security*
