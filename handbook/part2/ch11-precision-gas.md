# Chapter 11: Precision, Arithmetic & Gas Attacks

*"A single misplaced decimal point cost $394,000. The code was correct. The units were wrong. Nobody noticed until the treasury was full of money that belonged to users."*

---

## The Futureswap Incident: May 17, 2023

On May 17, 2023, a developer deployed a routine update to the Futureswap perpetual futures protocol. The update modified the fee calculation in the funding rate mechanism. The developer tested the update against the unit tests—all passed. The developer submitted the pull request—code review approved. The update was deployed.

Within hours, users began reporting that their trades were being charged extraordinary fees. A trader who should have paid $10 in funding fees was charged $100,000. Another who should have paid $50 was charged $500,000. The protocol's treasury was swelling with funds that did not belong to it.

The post-mortem identified the root cause in one paragraph. Futureswap used a fee parameter stored as a "wad"—a fixed-point number with 18 decimal places, where `1 ether = 1.0` and `0.003 ether = 0.003`. The fee was intended to be 0.3% (thirty basis points).

In one code path, the fee was correctly interpreted as a wad:

```solidity
// Correct: feeRateWad = 0.003 ether → 0.3%
uint256 fee = amount.mulWadDown(feeRateWad);
```

In another code path—the one added in the update—the same variable was divided by `10_000` as if it were basis points:

```solidity
// Bug: Interpreting a wad as basis points
uint256 fee = amount * feeRateWad / 10_000;
// feeRateWad = 0.003 ether = 3,000,000,000,000,000 (3e15)
// fee = amount * 3e15 / 10000 = amount * 3e11
// Intended: amount * 0.003 → Actual: amount * 300,000,000,000
```

The fee was **eleven orders of magnitude** too large. The developer who wrote the original `mulWadDown` code understood that `feeRateWad` was a wad. The developer who wrote the `/ 10_000` code did not. Both implementations passed code review because both were mathematically correct in isolation. Neither reviewer asked: *"what units is this variable in?"*

The total excess fees collected: approximately $394,000. Futureswap refunded every affected user from the protocol treasury. The financial loss was contained. The trust loss was not—users who had been charged 100,000x the expected fee did not return.

The lesson: **units are part of the type system, even when the language doesn't enforce them.** Every numeric variable carries implicit unit information that the compiler cannot check. The only defense is a naming convention that makes the units explicit—and a review process that treats unit errors as critical bugs.

---

## The Thetanuts Finance Incident: June 2026

On June 14, 2026, Thetanuts Finance—a decentralized options protocol on Ethereum—was exploited for approximately $2 million. The vulnerability was discovered and rescued by a whitehat bot before the attacker could fully drain the protocol.

The root cause: integer division by zero in the options pricing formula. Specifically, the `_calculatePremium()` function computed a denominator as `(spotPrice - strikePrice)`. When the spot price briefly equaled the strike price during a volatile market movement, the denominator became zero.

```solidity
// VULNERABLE: Division by zero when spotPrice == strikePrice
function _calculatePremium(uint256 spotPrice, uint256 strikePrice, uint256 amount) 
    internal pure returns (uint256) {
    uint256 denominator = spotPrice - strikePrice;  // Can be zero!
    return amount * PRECISION / denominator;  // Reverts with division by zero
}
```

In Solidity 0.8+, division by zero reverts. But the revert itself was the exploit vector. The attacker created an option with `spotPrice == strikePrice`, causing the premium calculation to revert. This blocked all subsequent option settlements, liquidations, and withdrawals that depended on the premium function. The protocol was not drained—it was frozen.

A whitehat bot detected the frozen state and submitted a transaction that changed the oracle price just enough to make `denominator != 0`, unfreezing the protocol. The attacker had already extracted $2 million before the freeze was detected, but the remaining $8 million was saved.

The Thetanuts incident demonstrates that precision errors are not limited to fee miscalculations. A division that can produce zero can become a denial-of-service vector when that division gates critical protocol functions.

---

## Why Precision Attacks Are Different

Precision vulnerabilities are unlike the other vulnerability classes in this book. Flash loan attacks are deliberate—the attacker constructs a multi-step transaction chain to exploit a known weakness. Reentrancy attacks are deliberate—the attacker crafts a callback to corrupt state. Oracle manipulation is deliberate—the attacker moves markets to exploit price feeds.

Precision loss is—usually—not.

The attacker does not *exploit* a precision bug. The precision bug *itself* is the attacker. It silently corrupts every calculation it touches, producing outputs that are close enough to correct that nobody notices—until the accumulated error becomes catastrophic.

This makes precision bugs uniquely dangerous for four reasons:

1. **They survive audits.** Auditors verify logic, not arithmetic precision. A function that divides `amount * rate / total` is logically correct. That it loses precision for small `amount` values is invisible to logic-focused review.

2. **They survive testing.** Unit tests use round numbers: 100 tokens, 10% rate, 1,000 total supply. Precision errors emerge at the edges: 1 token, 0.001% rate, 1,000,000 total supply. Standard test coverage misses the edges.

3. **They survive production use.** Most users interact with the protocol at normal volumes where precision loss is negligible. The bug lurks in the edge cases, waiting for a user with unusual parameters.

4. **When they manifest, they affect everyone.** A reentrancy bug drains one function. A precision bug corrupts every calculation that uses the affected math, across every user and every transaction.

---

## Pattern #25: Division Before Multiplication

**Severity**: MEDIUM → HIGH (context-dependent)
**Real cases**: Multiple DeFi protocols with rounding errors favoring attackers

### The Vulnerability

Solidity integers truncate toward zero. Dividing before multiplying amplifies truncation loss:

```solidity
// ❌ VULNERABLE: Division before multiplication truncates to zero
uint256 fee = (amount / totalStaked) * rewardRate;
// amount = 5, totalStaked = 100, rewardRate = 1000
// (5 / 100) * 1000 → 0 * 1000 → 0 ← user gets nothing

// ✅ SAFE: Multiplication before division preserves precision
uint256 fee = (amount * rewardRate) / totalStaked;
// (5 * 1000) / 100 → 5000 / 100 → 50 ← correct proportional share
```

The fix is mechanical: multiply first, divide last. But this introduces a new risk. If `amount * rewardRate` exceeds `type(uint256).max`, the multiplication overflows before the division can rescue it. This trade-off—precision versus overflow protection—is the fundamental tension in all fixed-point arithmetic.

### The Protocol-Favored Rounding Trap

Many protocols intentionally round down in their favor. A lending protocol might round the collateral value down and the borrow amount up—both safe directions. But when one code path rounds down and another rounds up on the same value, the protocol creates arbitrage:

```solidity
// Deposit: rounds collateral DOWN (safe for protocol)
uint256 collateralValue = amount.mulDivDown(price, PRECISION);

// Withdraw: rounds collateral UP (safe for protocol)
uint256 withdrawalValue = amount.mulDivUp(price, PRECISION);

// Attacker: deposits → withdraws → repeats
// Each cycle loses (mulDivUp - mulDivDown) / 2 per round
// The protocol is slowly drained by rounding arbitrage
```

The fix: use consistent rounding direction across all operations on the same value, OR make the rounding direction a parameter that the caller specifies.

### The Fix

```solidity
import "@openzeppelin/contracts/utils/math/Math.sol";

// mulDiv with overflow protection via 512-bit intermediate
uint256 fee = Math.mulDiv(amount, rewardRate, totalStaked);

// For rounding-sensitive operations, be explicit:
uint256 fee = Math.mulDiv(amount, rewardRate, totalStaked, Math.Rounding.Floor);
uint256 fee = Math.mulDiv(amount, rewardRate, totalStaked, Math.Rounding.Ceil);
```

---

## Pattern #26: Unsafe Downcast

**Severity**: MEDIUM → CRITICAL (if downcast value controls fund transfers)

### The Vulnerability

Solidity allows downcasting from larger integer types to smaller ones. The excess high-order bits are silently discarded—this is not a revert, not a warning, not even a compiler diagnostic by default:

```solidity
uint256 bigValue = type(uint128).max + 1;  // 2^128 = 340282366920938463463374607431768211456
uint128 smallValue = uint128(bigValue);    // Wraps to 0 — silently

// In a financial context:
uint256 actualCollateral = 2**128;  // ~3.4e38 — more than all money in existence
uint128 cappedCollateral = uint128(actualCollateral);  // Wraps to 0
// Protocol now believes user has 0 collateral
// All user positions immediately underwater → mass liquidation
```

Downcasting bugs are particularly dangerous because they manifest only at extreme values that are rare in testing but possible in production. A token with 18 decimals can easily produce amounts exceeding `type(uint128).max` if the token supply is large enough.

### The Fix

```solidity
import "@openzeppelin/contracts/utils/math/SafeCast.sol";

// Reverts on overflow instead of silent wrapping
uint128 safe = bigValue.toUint128();

// Or design defensively: use the larger type throughout
// If a value can grow beyond uint128, it should be uint256.
```

---

## Pattern #27: Unit Confusion

**Severity**: HIGH
**Real case**: Futureswap $394K (2023)
**Common in**: Any protocol that handles multiple token decimals

### The Vulnerability

A numeric value represents a quantity in specific units. The code treats it as if it's in different units. The result is off by orders of magnitude:

```solidity
uint256 public feeRate;  // What units? Wad? Basis points? Percentage? Raw integer?

function chargeFeeA(uint256 amount) external view returns (uint256) {
    return amount.mulWadDown(feeRate);  // Assumes feeRate is a wad (18 decimals)
}

function chargeFeeB(uint256 amount) external view returns (uint256) {
    return amount * feeRate / 10_000;   // Assumes feeRate is basis points (4 decimals)
}
// If feeRate = 0.003 ether (a wad):
// chargeFeeA: amount * 0.003 → correct
// chargeFeeB: amount * 3e15 / 10000 → amount * 3e11 → WRONG by 11 orders
```

The worst case is multi-token protocols where each token has different decimals. USDC has 6 decimals. ETH has 18. WBTC has 8. A function that normalizes all amounts to 18 decimals must convert each token correctly—and one missed conversion corrupts every subsequent calculation.

### The Fix

```solidity
// ✅ Names encode units — no ambiguity
uint256 public feeRateWad;     // 18 decimal places
uint256 public feeRateBps;     // 4 decimal places (basis points)
uint256 public exchangeRateRay; // 27 decimal places (Ray, used by MakerDAO)

uint256 public amountE18;      // 18 decimal (standard ERC20, ETH)
uint256 public amountE6;        // 6 decimal (USDC, USDT)
uint256 public amountE8;        // 8 decimal (WBTC)

// Every function MUST declare unit expectations in parameter names
function chargeFee(
    uint256 amountE18, 
    uint256 feeRateWad
) external pure returns (uint256 feeE18) {
    feeE18 = amountE18.mulWadDown(feeRateWad);
}
```

The naming convention is enforced by code review, not the compiler. This is why it must be absolute. Every variable that represents a numeric quantity MUST carry its unit suffix. PRs that omit suffixes are rejected. Period.

---

## Pattern #28: Unbounded Loop / Block Gas Limit

**Severity**: MEDIUM → CRITICAL (if loop permanently bricks a critical function)

### The Vulnerability

A loop iterates over a data structure whose size can grow without bound. When the size exceeds the block gas limit, the function becomes permanently unusable:

```solidity
// ❌ VULNERABLE: Grows with every user
address[] public stakers;

function distributeRewards() external {
    for (uint256 i = 0; i < stakers.length; i++) {
        uint256 reward = calculateReward(stakers[i]);
        token.transfer(stakers[i], reward);
    }
    // When stakers.length > ~500, gas exceeds block limit
    // Function is PERMANENTLY bricked. Funds are stuck.
}
```

This is not a theoretical concern. Multiple protocols have deployed contracts where the staker array grew until `distributeRewards()` became impossible to call. The only fix was a complete redeployment.

A subtler variant affects mappings with unbounded iteration. If the protocol must iterate over all entries in a mapping but the number of entries grows without bound, the iteration eventually exceeds the block gas limit.

### The Fix: Pull Over Push

```solidity
// ✅ SAFE: Each user pulls their own reward
mapping(address => uint256) public rewards;

function claimReward() external {
    uint256 reward = rewards[msg.sender];
    require(reward > 0, "No reward");
    rewards[msg.sender] = 0;  // CEI: effects before interactions
    token.transfer(msg.sender, reward);
}
```

If push is absolutely required, impose a hard iteration limit and provide a mechanism to process remaining items:

```solidity
uint256 public constant MAX_BATCH = 200;
uint256 public lastProcessedIndex;

function distributeRewardsBatch() external {
    uint256 end = lastProcessedIndex + MAX_BATCH;
    if (end > stakers.length) end = stakers.length;
    
    for (uint256 i = lastProcessedIndex; i < end; i++) {
        // process stakers[i]
    }
    
    lastProcessedIndex = end;
}
```

---

## Pattern #29: Hardcoded 2300 Gas Limit (`.transfer()` / `.send()`)

**Severity**: LOW → MEDIUM

### The Vulnerability

`.transfer()` and `.send()` forward exactly 2,300 gas to the recipient. This was recommended as a reentrancy defense from 2016-2019 (the "2,300 gas is not enough to re-enter" argument). It is now actively harmful:

```solidity
// ❌ DEPRECATED: Breaks smart contract wallets
payable(recipient).transfer(amount);
```

Smart contract wallets (Safe, Argent, Biconomy) need more than 2,300 gas to process a receive. Multi-signature wallets need more. Any contract with a `receive()` function that logs an event (which costs gas) needs more. The transfer silently fails. The user's funds are stuck.

### The Fix

```solidity
// ✅ SAFE: Forwards all available gas
(bool ok,) = payable(recipient).call{value: amount}("");
require(ok, "Transfer failed");
```

But `.call{}` forwards ALL available gas, which enables reentrancy. Always apply check-effects-interactions (Chapter 9) before using `.call{}`. Never use `.call{}` before finalizing state changes.

---

## Pattern #30: Division by Zero / Overflow Panics in Solidity 0.8+

**Severity**: HIGH (if revert bricks critical function)
**Real case**: Thetanuts Finance $2M (2026)

### The Vulnerability

Solidity 0.8+ panics on overflow and division by zero. This is generally safer than Solidity 0.7's silent wrapping. But in financial protocols, an unexpected panic in a critical function can freeze user funds:

```solidity
// VULNERABLE: Panics when spotPrice == strikePrice
function calculatePremium(uint256 spotPrice, uint256 strikePrice) 
    internal pure returns (uint256) {
    return amount * PRECISION / (spotPrice - strikePrice);
    // Solidity 0.8+ panics on division by zero
    // All functions that depend on calculatePremium() are bricked
}
```

The Thetanuts attacker deliberately created options at `spotPrice == strikePrice`, causing the premium calculation to panic. This blocked settlements, liquidations, and withdrawals across the entire protocol.

### The Fix

```solidity
function calculatePremium(uint256 spotPrice, uint256 strikePrice) 
    internal pure returns (uint256) {
    if (spotPrice == strikePrice) return 0;  // Handle edge case
    uint256 diff = spotPrice > strikePrice 
        ? spotPrice - strikePrice 
        : strikePrice - spotPrice;
    return amount * PRECISION / diff;
}
```

Every unchecked arithmetic operation must consider: *what happens at the extremes?* Zero denominators, maximum values, minimum values. The happy path is easy. The edge cases are where precision bugs become exploits.

---

## The Precision Checklist

```
□ Every numeric variable name encodes its unit.
  feeRateWad, amountE18, rateRay. No exceptions. Enforce in code review.

□ Every division has a documented rounding direction.
  "Rounds down" or "Rounds up" in the NatSpec. Not "because it's correct."

□ Every multiplication-before-division pair is checked for overflow.
  If amount * rate can exceed type(uint256).max, use mulDiv or widen to uint512.

□ Every downcast uses SafeCast or is proven safe.
  Never raw downcast. Even if it's "obviously" safe, the next developer may change the upstream value.

□ Every loop has a hard iteration limit or uses pull-over-push.
  If push is required, include a batching mechanism with continuation.

□ Every .transfer() / .send() has been replaced with .call{}.
  And every .call{} is preceded by CEI (check-effects-interactions).

□ Every unchecked arithmetic operation considers edge cases.
  What happens at zero? At max? When two values are equal? When the result underflows?
```

---

## Connection to Other Chapters

- **Ch4 (Flash Loans)**: Precision loss amplifies flash loan profitability. If rounding error means the attacker extracts 0.01% per cycle, and a flash loan enables 1,000 cycles per transaction, the 0.01% compounds to massive extraction.

- **Ch9 (Reentrancy)**: The gas forwarded by `.call{}` enables complex reentrancy chains. CEI must precede every `.call{}`. The 2,300 gas limit was a reentrancy defense that became a precision attack vector.

- **Ch10 (Initialization & Upgrades)**: Storage collisions during upgrades are precision errors in the storage dimension. Variable X at slot N means reserves in V1 and supply in V2. Every upgrade must verify storage layout precision.

- **Ch14 (MEV & Frontrunning)**: Gas griefing attacks are precision attacks on execution—the attacker consumes just enough gas to make the victim's transaction fail, extracting value from the failure.

---

*Next: Chapter 12 — Governance & Admin Attacks*
