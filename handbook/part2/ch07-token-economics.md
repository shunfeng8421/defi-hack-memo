# Chapter 7: Token Economics Attacks

*"The most dangerous vulnerability in DeFi is not in the code. It's in the assumptions."*

---

## The Warp Finance Paradox

On December 17, 2020, Warp Finance lost $7.8 million. The attack was clever, but the exploit report buried the real lesson.

Warp Finance allowed users to deposit Uniswap V2 LP tokens as collateral for loans. To value the LP tokens, the protocol calculated:

```
LP token value = (reserve0 × price0 + reserve1 × price1) / totalSupply
```

This formula is mathematically correct. Given the current reserves and current prices, it accurately computes the value of one LP share.

The attack did not break this formula. The attack exploited something the formula assumed: that the ratio of reserve0 to reserve1 reflected a market equilibrium. An attacker flash-loaned a massive amount of one token, swapped it into the pool, and changed the ratio. The formula faithfully reported the new, manipulated value. Warp Finance accepted it as collateral.

$7.8 million later, the lesson was clear: **a correct formula applied to manipulated inputs produces incorrect outputs.** The vulnerability was not in the valuation logic. It was in the assumption that the inputs were trustworthy.

---

## Pattern #13: Fee-on-Transfer Token Attack

**Severity**: HIGH

### The Vulnerability

Some tokens take a fee on every transfer. USDT is not one of them, but the standard allows it. If a protocol expects to receive 100 tokens from a transfer but the token contract actually delivers 97 (with a 3% fee), the protocol's internal accounting becomes wrong.

```solidity
// ❌ VULNERABLE: Assumes amount == actual received
function deposit(uint256 amount) external {
    token.transferFrom(msg.sender, address(this), amount);
    balances[msg.sender] += amount;  // Credits 100, received 97
    
    // Attacker can now withdraw more than they deposited
}
```

### The Attack

1. Attacker deposits 100 tokens → contract receives 97 (3% fee) → credits the attacker 100
2. Attacker withdraws 100 tokens → contract sends 100 → attacker received 97, withdrew 100
3. Attacker repeats until the contract's deficit is drained

### The Fix

```solidity
// ✅ SAFE: Uses actual received amount
function deposit(uint256 amount) external {
    uint256 balanceBefore = token.balanceOf(address(this));
    token.transferFrom(msg.sender, address(this), amount);
    uint256 received = token.balanceOf(address(this)) - balanceBefore;
    balances[msg.sender] += received;  // Credits what was actually received
}
```

---

## Pattern #14: Rebase Token Attack

**Severity**: HIGH

### The Vulnerability

Rebase tokens (like Ampleforth) change all holders' balances automatically. A protocol that caches a user's token balance may become outdated after a rebase event.

```solidity
// ❌ VULNERABLE: Cached balance may be stale after rebase
mapping(address => uint256) public cachedBalance;

function deposit(uint256 amount) external {
    token.transferFrom(msg.sender, address(this), amount);
    cachedBalance[msg.sender] += amount;  // Stale after next rebase
}
```

### The Fix

Always read the token's current balance rather than relying on cached values:

```solidity
function deposit(uint256 amount) external {
    uint256 before = token.balanceOf(address(this));
    token.transferFrom(msg.sender, address(this), amount);
    uint256 received = token.balanceOf(address(this)) - before;
    // Use received, not amount
}
```

---

## Pattern #15: Mint/Burn Asymmetry

**Severity**: MEDIUM

### The Vulnerability

A protocol's `mint()` and `burn()` functions use different accounting methods. Over time, the total supply drifts away from the sum of all user balances.

```solidity
function mint(address to, uint256 amount) external onlyVault {
    _mint(to, amount);
    totalMinted += amount;
}

function burn(address from, uint256 amount) external onlyVault {
    _burn(from, amount);
    totalBurned += amount * 95 / 100;  // BUG: Burns 95%, not 100%
}
```

This creates a persistent leak — tokens are created but not fully destroyed. The protocol's accounting becomes permanently wrong.

### The Fix

Mint and burn must be symmetric:

```solidity
function burn(address from, uint256 amount) external onlyVault {
    _burn(from, amount);
    totalBurned += amount;  // Must match mint exactly
}
```

---

## Pattern #16: Permit Without Nonce

**Severity**: MEDIUM
**Real case**: Multiple DEX router exploits

### The Vulnerability

ERC-2612 `permit()` allows gasless token approvals via off-chain signatures. The signature includes:

```solidity
bytes32 public constant PERMIT_TYPEHASH = keccak256(
    "Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"
);
```

If the `nonce` is missing from the type definition — or if it's always zero — the signature is valid forever within the deadline window. An attacker who observes the signature in the mempool can replay it.

### The Fix

Always include nonce, always use it:

```solidity
// ✅ SAFE: Nonce explicitly included and validated
require(nonce == nonces[owner]++, "Invalid nonce");
```

---

## The Token Economics Detector

| Pattern | Name | Detection |
|:--:|------|------|
| 13 | Fee-on-Transfer | `transferFrom` + credit `amount` (not actual) |
| 14 | Rebase | `balanceOf` cached in storage |
| 15 | Mint/Burn Drift | `mint` and `burn` with different formulas |
| 16 | Permit/Nonce | `permit` + `struct` without `nonce` field |

---

## The Token Integration Checklist

Before integrating any token into your protocol:

1. **Does the token take fees?** Test with a small transfer and verify the received amount equals the transferred amount.
2. **Does the token rebase?** Check if `balanceOf` can change without a `transfer` event.
3. **Does the token have a callback?** ERC-777 and ERC-1155 tokens call back into the sender's contract. This creates a reentrancy vector.
4. **Does the token return a value?** Some tokens return `false` instead of reverting on failure. Always check return values.
5. **Can the token be paused?** If your protocol depends on a token that can be paused by its admin, your protocol depends on that admin.
6. **Can the token be upgraded?** Proxy-based tokens can change their implementation arbitrarily.

---

*Next: Chapter 8 — Cross-Chain Vulnerabilities*
