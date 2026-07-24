# Chapter 11: Precision, Arithmetic & Gas Attacks

*"A single misplaced decimal point cost $394,000. The code was correct. The units were wrong."*

---

## The Futureswap Incident

On May 17, 2023, the Futureswap protocol was exploited for $394,000. The post-mortem was one sentence long. The vulnerability was a precision error: a fee rate stored as a wad (18 decimal places) was interpreted as basis points (2 decimal places). Every fee charged was 10,000 times larger than intended.

Users who should have paid $10 in fees paid $100,000. The excess fees went to the protocol's treasury. The protocol itself was the attacker, unintentionally.

The precision loss class of vulnerabilities is subtle because the code is logically correct. The arithmetic works. The formulas are sound. The error is not in the logic — it is in the unit representation. One number means different things in different contexts, and the code does not enforce which context is correct.

---

## Pattern #25: Precision Loss

**Severity**: MEDIUM — HIGH (depending on financial impact)

### The Vulnerability

Solidity does not have floating-point numbers. All calculations use integers. Division truncates toward zero. The order of operations determines how much precision is lost.

```solidity
// ❌ VULNERABLE: Division before multiplication
uint256 fee = (amount / totalStaked) * rewardRate;
// amount = 5, totalStaked = 100, rewardRate = 100
// (5 / 100) * 100 = 0 * 100 = 0 → fee = 0!

// ✅ SAFE: Multiplication before division
uint256 fee = (amount * rewardRate) / totalStaked;
// (5 * 100) / 100 = 500 / 100 = 5 → fee = 5
```

The fix is always the same: multiply first, divide last. But this fix is fragile. If `amount * rewardRate` exceeds `type(uint256).max`, the multiplication overflows before the division can rescue it.

### The Deeper Problem: Unit Confusion

The harder case is when two numbers have different implied decimal places:

```solidity
// feeRateWad = 0.003 ether = 3000000000000000 wei (18 decimals)
// Intended fee: 0.3%
// Actual: interpreted as 3% in one place, 30% in another

// BUG: Treating a wad as basis points
uint256 fee = (amount * feeRateWad) / 10000;
// feeRateWad = 3000000000000000, amount = 1 ether
// fee = 1e18 * 3e15 / 10000 = 3e29 → massive overflow or wrong value
```

### The Fix

Unit names in variable names. Always.

```solidity
// Unit-name convention: variableNameUnit
uint256 public feeRateWad;     // 18 decimal places
uint256 public feeRateBps;     // 4 decimal places (basis points)
uint256 public feeRateRay;     // 27 decimal places

// Every calculation must convert to a common unit
uint256 feeWad = amountWad.mulWadDown(feeRateWad);
```

---

## Pattern #26: Unsafe Downcast

**Severity**: MEDIUM

### The Vulnerability

Solidity allows implicit downcasting from `uint256` to `uint128`, but the value silently wraps:

```solidity
uint256 bigValue = type(uint128).max + 1;  // 2^128
uint128 smallValue = uint128(bigValue);     // Wraps to 0!
```

If this happens in a financial calculation, the result is a zero-value asset where a large-value asset was expected.

### The Fix

OpenZeppelin's `SafeCast` library:

```solidity
import "@openzeppelin/contracts/utils/math/SafeCast.sol";

uint128 smallValue = bigValue.toUint128();  // Reverts if overflow
```

---

## Pattern #27: Hardcoded Gas Limit

**Severity**: LOW

### The Vulnerability

`.transfer()` and `.send()` forward exactly 2,300 gas to the recipient. If the recipient is a contract that needs more gas — a multi-sig wallet, a smart contract wallet, or any contract with a complex receive function — the transfer fails.

```solidity
// ❌ VULNERABLE: Fails on contract wallets
payable(recipient).transfer(amount);  // Only 2,300 gas
```

This was the recommended pattern for years. It is now considered harmful because it breaks composability with smart contract wallets.

### The Fix

```solidity
// ✅ SAFE: Forwards all available gas
(bool success,) = payable(recipient).call{value: amount}("");
require(success, "Transfer failed");
```

But this introduces a reentrancy risk — `.call{}` forwards all gas, allowing complex callback logic. Always apply CEI before using `.call{}`.

---

## Pattern #28: Unbounded Loop DoS

**Severity**: MEDIUM

### The Vulnerability

A loop iterates over a user-controlled array with no maximum size. The attacker adds enough items that the gas cost exceeds the block gas limit. The function becomes permanently unusable.

```solidity
// ❌ VULNERABLE: No iteration limit
function distributeRewards(address[] calldata recipients, uint256[] calldata amounts) external {
    for (uint256 i = 0; i < recipients.length; i++) {
        token.transfer(recipients[i], amounts[i]);
    }
}
```

If `recipients.length` is 10,000, the loop costs more than the block gas limit. The transaction reverts. Nobody can claim their reward.

### The Fix

```solidity
// ✅ SAFE: Pull over push pattern
function claimReward(uint256 index, bytes32[] calldata proof) external {
    require(!claimed[index], "Already claimed");
    require(verifyMerkleProof(index, msg.sender, proof), "Invalid proof");
    claimed[index] = true;
    token.transfer(msg.sender, rewardAmount);
}
```

Instead of the contract pushing rewards to everyone, each user pulls their own reward. The gas cost is distributed across individual transactions.

---

## Pattern #29: Phantom Fallback

**Severity**: MEDIUM

### The Vulnerability

A contract has a `fallback()` function that accepts any call without reverting:

```solidity
fallback() external payable {}
```

Any accidental ETH transfer (a user sends ETH to the wrong address, a DEX sends ETH as part of a swap, a bridge forwards ETH to the wrong destination) is silently accepted. The funds are locked in the contract forever because there is no withdrawal mechanism.

### The Fix

Either reject unexpected calls:

```solidity
fallback() external payable {
    revert("Unexpected call");
}
```

Or implement a rescue mechanism:

```solidity
function rescue(address token, uint256 amount) external onlyOwner {
    IERC20(token).transfer(owner, amount);
}
```

---

## The Precision & Gas Checklist

1. **Does every division have a rounding direction?** Up or down — never ambiguous.
2. **Are all numeric variable names annotated with their unit?** `amountWad`, `feeBps`, `rateRay`.
3. **Are all downcasts using SafeCast?** No silent wrapping.
4. **Do all loops have a gas limit?** Either a hard maximum or pull-over-push.
5. **Does the fallback function reject or rescue?** Never silently accept.

---

*Next: Chapter 12 — Governance & Admin Attacks*
