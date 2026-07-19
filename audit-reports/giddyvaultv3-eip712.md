# giddyvaultv3 $1.3M — EIP-712 Type Incompleteness

**Found by**: Shiqiang Chen | **Date**: July 19, 2026
**Pattern**: #27 EIP-712 Type Mismatch — **validates our Paper #08**

## Root Cause

```solidity
// ⚠️ BUG: TYPEHASH 只包含 bytes[] data 的哈希
bytes32 constant VAULTAUTH_TYPEHASH =
    keccak256("VaultAuth(bytes32 nonce,uint256 deadline,uint256 amount,bytes[] data)");
```

The `SwapInfo` struct contains:
```solidity
struct SwapInfo {
    address fromToken;  // ⚠️ NOT in the TYPEHASH
    address toToken;    // ⚠️ NOT in the TYPEHASH
    uint256 amount;     // ⚠️ NOT in the TYPEHASH (separate from outer amount)
    address aggregator; // ⚠️ NOT in the TYPEHASH
    bytes data;         // Only this is hashed
}
```

## Attack

1. User signs `VaultAuth(nonce, deadline, amount, keccak256(data))`
2. Attacker replaces `fromToken`, `toToken`, `amountInData`, `aggregator`
3. `keccak256(data)` is unchanged → **signature still valid**
4. Compound call approves attacker for `uint256.max`
5. Attacker drains gauge tokens from strategy

## Why This Validates Our Research

This is the **third** EIP-712 error we've found in production:

| Protocol | Bug | Loss |
|------|------|--:|
| PresidentElector | `uint256[]` vs `address[]` mismatch | N/A |
| SnowmanAirdrop | `"addres"` typo | N/A |
| **giddyvaultv3** | **keccak256(data) excludes struct fields** | **$1.3M** |

Our Paper #08 (EIP-712 Systemic Errors) predicted exactly this vulnerability class. This is the first confirmed high-value exploit of this pattern.

## Detection

✅ Scanner Pattern #27 fires on EIP-712 TYPEHASH with `bytes[] data` (unstable encoding)

---

**Today: 3 new finds** | **12 total vulnerabilities** | **$54.62M**
