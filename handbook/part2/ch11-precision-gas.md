# Chapter 11: Precision, Arithmetic & Gas Attacks

*"A single misplaced decimal point cost $394,000. The code was correct. The units were wrong."*

---

## The Futureswap Incident

On May 17, 2023, the Futureswap protocol was exploited for approximately $394,000. The post-mortem was shorter than this paragraph. The root cause would never appear in a typical audit report because the code was logically flawless.

Futureswap used a fee parameter stored as a "wad"—a fixed-point number with 18 decimal places, where `1 ether = 1.0` and `0.003 ether = 0.003`. The fee was intended to be 0.3%—thirty basis points.

In one code path, the fee was interpreted as a wad:
```solidity
// Correct: feeRateWad = 0.003 ether → 0.3%
uint256 fee = amount.mulWadDown(feeRateWad);
```

In another code path, the same variable was divided by `10_000` as if it were basis points:
```solidity
// Bug: Interpreting a wad as basis points
uint256 fee = amount * feeRateWad / 10_000;
// feeRateWad = 0.003 ether = 3,000,000,000,000,000 (3e15)
// fee = amount * 3e15 / 10000 = amount * 3e11
// Intended: amount * 0.003. Actual: amount * 300,000,000,000
```

The fee was eleven orders of magnitude larger than intended. Users who should have paid $10 in fees were charged $100,000. The excess went to the protocol's treasury. Futureswap was not attacked—it was accidentally predatory.

The developer who wrote the `mulWadDown` version understood the unit. The developer who wrote the `/ 10_000` version did not. Both versions passed code review because both versions were "correct" in isolation. Neither reviewer asked: "what units is this variable in?"

---

## Why Precision Attacks Are Different

Precision vulnerabilities are not like the others in this book. Flash loan attacks are deliberate. Reentrancy attacks are deliberate. Oracle manipulation is deliberate. Precision loss is—usually—not.

The attacker does not exploit a precision bug. The precision bug itself is the attacker. It silently corrupts every calculation it touches, producing outputs that are close enough to correct that nobody notices—until the accumulated error becomes catastrophic.

This makes precision bugs uniquely dangerous. They survive audits. They survive testing. They survive months of production use. And when they finally manifest, they affect every user simultaneously.

---

## Pattern #25: Division Before Multiplication

**Severity**: MEDIUM

### The Vulnerability

Solidity integers truncate toward zero. Dividing before multiplying amplifies this truncation:

```solidity
// ❌ VULNERABLE: Division before multiplication
uint256 fee = (amount / totalStaked) * rewardRate;
// amount = 5, totalStaked = 100, rewardRate = 100
// (5 / 100) * 100 → 0 * 100 → 0

// ✅ SAFE: Multiplication before division
uint256 fee = (amount * rewardRate) / totalStaked;
// (5 * 100) / 100 → 500 / 100 → 5
```

The fix is mechanical: multiply first, divide last. But this is fragile. If `amount * rewardRate` exceeds `type(uint256).max`, the multiplication overflows before the division can rescue it. This trade-off—precision versus overflow protection—is the fundamental tension in fixed-point arithmetic.

### The Fix

Use a math library that handles both:

```solidity
import "@openzeppelin/contracts/utils/math/Math.sol";

uint256 fee = Math.mulDiv(amount, rewardRate, totalStaked);
// Internally: (amount * rewardRate) / totalStaked
// With overflow protection via 512-bit intermediate
```

---

## Pattern #26: Unsafe Downcast

**Severity**: MEDIUM

### The Vulnerability

Solidity allows downcasting from larger integer types to smaller ones. The excess bits are silently discarded:

```solidity
uint256 bigValue = type(uint128).max + 1;  // 2^128 = 340282366920938463463374607431768211456
uint128 smallValue = uint128(bigValue);    // Wraps to 0!
```

If the downcast value is used in a financial calculation—a collateral amount, a loan value, a reward—the result is zero where a massive value was expected.

### The Fix

Use OpenZeppelin's `SafeCast`:

```solidity
uint128 smallValue = bigValue.toUint128();  // Reverts if overflow
```

---

## Pattern #27: Unit Confusion

**Severity**: HIGH
**Real case**: Futureswap $394K

### The Vulnerability

A numeric value represents a quantity in specific units. The code treats it as if it is in different units. The result is off by orders of magnitude.

```solidity
uint256 public feeRate;  // What units?

function chargeFeeA(uint256 amount) external {
    fee = amount.mulWadDown(feeRate);  // Assumes feeRate is a wad (18 decimals)
}

function chargeFeeB(uint256 amount) external {
    fee = amount * feeRate / 10_000;   // Assumes feeRate is basis points (4 decimals)
}
```

Two functions use the same variable in incompatible ways. Both are individually correct. Together, they are wrong.

### The Fix

Unit names in variable names. Always. No exceptions:

```solidity
// ✅ Names encode units
uint256 public feeRateWad;     // 18 decimal places
uint256 public feeRateBps;     // 4 decimal places (basis points)
uint256 public exchangeRateRay; // 27 decimal places
uint256 public amountE18;      // 18 decimal (standard ERC20)
uint256 public amountE6;        // 6 decimal (USDC, USDT)

// Every function must declare its unit expectations
function chargeFee(uint256 amountE18, uint256 feeRateWad) external pure returns (uint256 feeE18) {
    feeE18 = amountE18.mulWadDown(feeRateWad);
}
```

---

## Pattern #28: Unbounded Loop

**Severity**: MEDIUM

### The Vulnerability

A loop iterates over a user-controlled array with no maximum size. If the array contains 10,000 elements, the loop costs more than the block gas limit. The function becomes permanently unusable.

```solidity
// ❌ VULNERABLE: No iteration limit
function distributeRewards(address[] calldata recipients, uint256[] calldata amounts) external {
    for (uint256 i = 0; i < recipients.length; i++) {
        token.transfer(recipients[i], amounts[i]);
    }
}
```

### The Fix

The pull-over-push pattern: each user pulls their own reward, rather than the contract pushing to everyone:

```solidity
function claimReward(uint256 index, bytes32[] calldata proof) external {
    require(!claimed[index], "Already claimed");
    require(verifyProof(index, msg.sender, proof), "Invalid proof");
    claimed[index] = true;
    token.transfer(msg.sender, rewardAmount);
}
```

If push is required, impose a hard limit:

```solidity
function distributeRewards(address[] calldata recipients, uint256[] calldata amounts) external {
    require(recipients.length <= 200, "Batch too large");
    for (uint256 i = 0; i < recipients.length; i++) { ... }
}
```

---

## Pattern #29: Hardcoded Gas Limit (2300)

**Severity**: LOW

### The Vulnerability

`.transfer()` and `.send()` forward exactly 2,300 gas. If the recipient is a contract wallet, multi-sig, or any contract with a `receive()` function that does more than log an event, the transfer fails.

```solidity
// ❌ VULNERABLE: Fails on smart contract wallets
payable(recipient).transfer(amount);
```

This was recommended practice for years. It is now considered harmful because it breaks smart contract wallets that need more than 2,300 gas to process an incoming transfer.

### The Fix

```solidity
// ✅ SAFE: Forwards all available gas
(bool ok,) = payable(recipient).call{value: amount}("");
require(ok, "Transfer failed");
```

But `.call{}` introduces reentrancy risk—it forwards all gas, enabling complex callback logic. Always apply CEI (Ch9) before using `.call{}`.

---

## Pattern #30: Phantom Fallback

**Severity**: MEDIUM

### The Vulnerability

A contract has a `fallback()` function that silently accepts any call:

```solidity
fallback() external payable {}
```

Any accidental ETH transfer—a user sends to the wrong address, a DEX forwards ETH as part of a swap, a bridge forwards to the wrong destination—is silently absorbed. The funds are permanently locked because no withdrawal mechanism exists.

### The Fix

```solidity
// Option A: Reject unexpected calls
fallback() external payable {
    revert("Unexpected call");
}

// Option B: Rescue mechanism
function rescueETH() external onlyOwner {
    payable(owner).transfer(address(this).balance);
}
```

---

## The Precision Checklist

1. **Every numeric variable name encodes its unit.** `feeRateWad`, `amountE18`, `rateRay`.
2. **Every arithmetic operation uses a checked library.** `SafeCast`, `Math.mulDiv`, `FixedPoint`.
3. **Every division has a documented rounding direction.** "Rounds down in favor of the protocol" is a design decision.
4. **Every loop has a hard iteration limit or pull-over-push.** Never iterate a user-controlled array.
5. **Every transfer uses `.call{}` or a library that checks return values.** Never `.transfer()`.

---

## Connection to Other Chapters

- **Ch4 (Flash Loans)**: Precision loss can amplify flash loan profitability. If a 0.01% precision error means the attacker profits $100,000, a flash loan makes the attack zero-cost.
- **Ch9 (Reentrancy)**: The gas forwarded by `.call{}` enables reentrancy. CEI must always precede `.call{}`.
- **Ch10 (Initialization)**: Storage collisions during upgrades are precision errors. A variable at slot N means one thing in V1 and a completely different thing in V2.

---

*Next: Chapter 12 — Governance & Admin Attacks*
