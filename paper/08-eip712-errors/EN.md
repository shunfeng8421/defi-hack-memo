# When Type Hashes Lie — EIP-712 Implementation Errors in DeFi: Evidence from Competitive Audits

**Shiqiang Chen**  
*July 2026*

---

## Abstract

EIP-712 (Typed Structured Data Hashing and Signing) is the standard for gasless meta-transactions in Ethereum. Correct implementation requires exact alignment between the `TYPEHASH` constant and the function's parameter types — a one-character typo silently breaks all EIP-712 tooling compatibility. Through competitive security audits of 6 smart contract protocols, we discovered that 2 out of 2 contracts implementing EIP-712 contained critical TYPEHASH errors: a type mismatch (`uint256[]` instead of `address[]`) and a spelling error (`"addres"` instead of `"address"`). Both errors render standard EIP-712 signing libraries (ethers.js, viem, web3.js) completely incompatible with the contract, without triggering compiler warnings or runtime errors. We classify 5 categories of EIP-712 implementation errors, provide detection methodology and a Slither detector, and argue that EIP-712 errors represent a systematically underestimated risk in DeFi security.

---

## 1. Introduction

EIP-712 enables users to sign typed data off-chain, with the signature verified on-chain for gasless transactions. The standard is widely adopted: Uniswap's permit(), OpenSea's listing signatures, and DAO voting all depend on EIP-712.

The security of EIP-712 depends entirely on a simple but unforgiving invariant: the `TYPEHASH` constant computed by the Solidity contract MUST exactly match the typed data hash computed by the signing library. A single character error — a missing letter, a wrong type — silently breaks this invariant.

Unlike reentrancy or integer overflow, EIP-712 errors produce **no compiler warnings, no runtime errors, and no obvious test failures**. The contract deploys successfully. Function calls appear to succeed. But every meta-transaction from standard tooling will fail — and the developer may never know why.

---

## 2. Error Taxonomy

We identify 5 categories of EIP-712 implementation errors:

### Type 1: Spelling Errors ("Typo Hash")
```solidity
// ❌ ERROR
bytes32 constant TYPEHASH = keccak256(
    "claimTokens(addres recipient, uint256 amount)"  // "addres" not "address"
);
// ✅ CORRECT
bytes32 constant TYPEHASH = keccak256(
    "claimTokens(address recipient, uint256 amount)"
);
```
**Found in**: SnowmanAirdrop (CodeHawks 2025)
**Effect**: ethers.js `_signTypedData()` computes a different TYPEHASH — signature never verifies.

### Type 2: Type Mismatch
```solidity
// ❌ ERROR
bytes32 constant TYPEHASH = keccak256(
    "voteForCandidate(uint256[])"  // uint256[] — but parameter is address[]
);
// Function parameter:
function vote(address[] memory candidates) { ... }
// ✅ CORRECT
bytes32 constant TYPEHASH = keccak256(
    "voteForCandidate(address[])"  // Must match actual parameter types
);
```
**Found in**: PresidentElector (CodeHawks 2025)
**Effect**: `abi.encode(TYPEHASH, address[])` ≠ `abi.encode(TYPEHASH_with_uint256, uint256[])` — hash mismatch.

### Type 3: Missing Parameter
```solidity
// ❌ ERROR
bytes32 constant TYPEHASH = keccak256(
    "Transfer(address to, uint256 amount)"  // Missing 'address from'
);
```

### Type 4: Wrong Parameter Order
```solidity
// ❌ ERROR
bytes32 constant TYPEHASH = keccak256(
    "Swap(uint256 amountOut, uint256 amountIn)"  // Reversed
);
// Function: swap(uint256 amountIn, uint256 amountOut)
```

### Type 5: Missing `string` vs `bytes` Distinction
```solidity
// ❌ ERROR
bytes32 constant TYPEHASH = keccak256(
    "register(string name)"  // EIP-712 uses 'string' for UTF-8
);
// → ethers.js may use 'bytes' in some versions → mismatch
```

---

## 3. Empirical Evidence

We analyzed 6 smart contract protocols during competitive security audits:

| Protocol | Has EIP-712? | Error | Type |
|------|:--:|------|:--:|
| ThunderLoan | No | N/A | - |
| BossBridge | Yes (ECDSA, not EIP-712) | No TYPEHASH | - |
| vault-core | No | N/A | - |
| NFTDealers | No | N/A | - |
| **SnowmanAirdrop** | ✅ Yes | "addres" typo | Type 1 |
| **PresidentElector** | ✅ Yes | uint256[] vs address[] | Type 2 |

**Finding**: 2/6 contracts used EIP-712. **Both (100%)** contained critical implementation errors.

### Why This Matters

This is not a random sample — these are contest contracts from CodeHawks, a platform where professional auditors scrutinize code. If the error rate is 100% in audited contest contracts, the rate in production contracts (with less oversight) is likely higher.

---

## 4. Why These Errors Persist

EIP-712 errors are invisible to standard development workflows:

1. **No compiler warning**: Solidity compiles "addres" as a valid string
2. **No runtime error**: The contract deploys and operates normally
3. **Self-consistency trap**: If the same typo is in both TYPEHASH and signing code, it works — but only with custom tooling
4. **Testing gap**: Unit tests typically sign with custom code (matching the typo), not standard libraries
5. **Documentation complexity**: EIP-712 has subtle rules about `string` vs `bytes`, array encoding, and struct nesting

---

## 5. Detection

### 5.1 Slither Detector
Our `eip712-typo` Slither rule detects Type 1 and Type 2 errors:
- Flags TYPEHASH definitions containing `uint256[]` when the surrounding code has `address[]`
- Flags common spelling errors: `addres`, `amout`, `recipent`, `adress`

### 5.2 Manual Audit Checklist
- [ ] TYPEHASH string exactly matches Solidity function signature
- [ ] Parameter types match: `address` vs `uint256`, `uint256[]` vs `address[]`
- [ ] Parameter names match (optional but best practice)
- [ ] Test with ethers.js `_signTypedData()`, not custom hash computation
- [ ] Verify signature on-chain using generated test data

---

## 6. Related Work

No prior academic work has systematically studied EIP-712 implementation errors. Audit reports occasionally flag these issues, but the frequency and impact are undocumented. This paper provides the first classification and empirical evidence.

---

## 7. Conclusion

EIP-712 TYPEHASH errors represent a critically underappreciated risk in DeFi. With a 100% error rate in our audit sample, we argue that every EIP-712 implementation should be manually verified against standard signing libraries. We provide a 5-category taxonomy, detection tooling, and an audit checklist to address this gap.

The fix is trivial — change one string. But finding the error requires knowing to look.

---

**Audit Reports**: github.com/shunfeng8421/defi-hack-memo  
**Slither Detectors**: 50-rule DeFi scanner with `eip712-typo` rule
