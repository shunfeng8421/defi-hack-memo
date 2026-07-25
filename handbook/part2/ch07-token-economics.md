# Chapter 7: Token Economics Attacks

*"A correct formula applied to manipulated inputs produces incorrect outputs. The vulnerability is not in the calculation. It is in the assumption."*

---

## The Warp Finance Paradox

On December 17, 2020, Warp Finance lost $7.8 million. The attack did not break any code. Every function executed exactly as designed. Every mathematical formula produced the correct result. The vulnerability was not in the implementation—it was in the integration of two systems that were never designed to work together.

Warp Finance allowed users to deposit Uniswap V2 LP tokens as collateral for loans. To value the LP tokens, the protocol used a standard formula:

```solidity
uint256 lpValue = (reserve0 * price0 + reserve1 * price1) / totalSupply;
```

This formula is mathematically correct. Given the current reserves and current prices, it accurately computes the value of one LP share. The problem was that the formula's inputs—the reserves—could be changed by anyone, at any time, for the cost of a swap.

An attacker flash-loaned a massive amount of ETH, swapped it into the Uniswap pool, and changed the reserve ratio. The formula faithfully reported the new, manipulated value. Warp Finance accepted it as collateral. The attacker borrowed against this inflated valuation and walked away with $7.8 million in real assets.

The lesson: **a token's stated amount is not the same as the token's actual value. Every protocol that integrates external tokens must verify not just that a transfer succeeded, but that the token behaves as expected.**

---

## Pattern #12: Fee-on-Transfer Token Attack

**Severity**: HIGH

### The Vulnerability

Some tokens charge a fee on every transfer. When a user transfers 100 tokens, the recipient receives 97—the other 3 are burned, redistributed, or sent to a fee recipient. If a protocol's internal accounting assumes it received 100 tokens when it actually received 97, a deficit accumulates.

```solidity
// ❌ VULNERABLE: Assumes amount == actual received
function deposit(uint256 amount) external {
    token.transferFrom(msg.sender, address(this), amount);
    // If token has 3% fee, contract received 97, not 100
    balances[msg.sender] += amount;  // Credits 100
    // Protocol now owes 3 tokens more than it has
}
```

Each deposit creates a small deficit. Over hundreds of deposits, the deficit compounds. The attacker can exploit this by repeatedly depositing and withdrawing until the protocol's reserves are drained.

### The Attack

1. Attacker deposits 100 tokens → protocol receives 97 (3% fee) → credits the attacker 100
2. Attacker withdraws 100 tokens → protocol sends 100 → net loss per cycle: 3 tokens
3. Attacker repeats until the protocol's token balance reaches zero

### The Fix

Never trust the `amount` parameter. Always measure what was actually received:

```solidity
// ✅ SAFE: Measures actual received amount
function deposit(uint256 amount) external {
    uint256 balanceBefore = token.balanceOf(address(this));
    token.transferFrom(msg.sender, address(this), amount);
    uint256 received = token.balanceOf(address(this)) - balanceBefore;
    balances[msg.sender] += received;  // Credits what was actually received
    require(received > 0, "Zero received");
}
```

This pattern neutralizes fee-on-transfer tokens, rebase tokens, and any other token mechanism that causes the received amount to differ from the stated amount.

### Detection

The 58-pattern scanner detects this pattern when a function uses `transferFrom` with `amount` as the credited value, without measuring a before/after balance delta.

---

## Pattern #13: Rebase Token Attack

**Severity**: HIGH

### The Vulnerability

Rebase tokens—such as Ampleforth (AMPL)—automatically adjust all holder balances to target a specific price. When a rebase occurs, every holder's balance changes without a corresponding `Transfer` event. A protocol that caches a user's token balance in its own storage will hold stale data after a rebase.

```solidity
// ❌ VULNERABLE: Cached balance may be stale after rebase
mapping(address => uint256) public stakedBalances;

function stake(uint256 amount) external {
    token.transferFrom(msg.sender, address(this), amount);
    stakedBalances[msg.sender] += amount;
    // Next rebase: token.balanceOf(address(this)) changes, but stakedBalances does not
    // Protocol is now out of sync with reality
}
```

### The Attack

1. User stakes 100 AMPL → protocol records `stakedBalances[user] = 100`
2. Rebase occurs → 100 AMPL becomes 110 AMPL (positive rebase) or 90 AMPL (negative rebase)
3. User's true stake is now 110, but protocol thinks it is 100
4. User withdraws "100" → protocol sends 100 from a pool that actually contains 110
5. Repeat → protocol's accounting drifts permanently away from reality

### The Fix

Use shares instead of absolute amounts:

```solidity
// ✅ SAFE: Share-based accounting immune to rebase
function stake(uint256 amount) external {
    uint256 before = token.balanceOf(address(this));
    token.transferFrom(msg.sender, address(this), amount);
    uint256 received = token.balanceOf(address(this)) - before;
    
    uint256 sharesToMint = totalSupply == 0
        ? received
        : received * totalSupply / totalAssets;
    
    _mint(msg.sender, sharesToMint);
    totalAssets += received;
}

function unstake(uint256 shares) external {
    uint256 assets = shares * totalAssets / totalSupply;
    _burn(msg.sender, shares);
    totalAssets -= assets;
    token.transfer(msg.sender, assets);
}
```

With shares, every holder's ownership percentage remains constant regardless of rebases. The `totalAssets` variable tracks what the contract actually holds, not what it was told it received.

---

## Pattern #14: Mint/Burn Asymmetry

**Severity**: MEDIUM

### The Vulnerability

A protocol's `mint()` and `burn()` functions use different accounting methods. Over time, the total supply diverges from the sum of all balances.

```solidity
// ❌ VULNERABLE: Asymmetric mint and burn
function mint(address to, uint256 amount) external onlyVault {
    _mint(to, amount);
    totalMinted += amount;  // Full amount recorded
}

function burn(address from, uint256 amount) external onlyVault {
    _burn(from, amount);
    totalBurned += amount * 95 / 100;  // BUG: Only records 95%!
}
```

Every burn records less destruction than actually happened. The `totalMinted - totalBurned` no longer equals `totalSupply`. Anyone relying on this invariant will make incorrect decisions.

### The Fix

Mint and burn must be perfectly symmetric:

```solidity
function mint(address to, uint256 amount) external onlyVault {
    _mint(to, amount);
    totalMinted += amount;
}

function burn(address from, uint256 amount) external onlyVault {
    _burn(from, amount);
    totalBurned += amount;  // Must match mint exactly
}
```

If a fee is intended, collect it explicitly as a separate transfer rather than embedding it in the burn calculation.

---

## Pattern #15: Permit Without Nonce

**Severity**: MEDIUM
**Real cases**: Multiple DEX router exploits

### The Vulnerability

ERC-2612 `permit()` allows gasless token approvals via off-chain signatures. The signature includes fields like `owner`, `spender`, `value`, and `deadline`. If the `nonce` field is missing from the signed type definition—or if it is always zero—the signature is valid forever within the deadline window.

```solidity
// ❌ VULNERABLE: Signed struct without nonce
bytes32 constant PERMIT_TYPEHASH = keccak256(
    "Permit(address owner,address spender,uint256 value,uint256 deadline)"
    // Missing: uint256 nonce
);
```

Without a nonce, every signature is valid until its deadline expires. An attacker who observes a signature in the mempool can replay it at any time before the deadline.

### The Fix

Always include nonce in the signed type and always validate it:

```solidity
// ✅ SAFE: Nonce included and validated
bytes32 constant PERMIT_TYPEHASH = keccak256(
    "Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"
);

function permit(address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s) external {
    require(block.timestamp <= deadline, "Expired");
    require(nonces[owner] == _useNonce(owner), "Invalid nonce");  // Auto-increments
    // ... verify signature
}
```

---

## The Token Integration Checklist

1. **Does the token take fees?** Test with a small transfer. Verify `balanceAfter - balanceBefore == amount`.
2. **Does the token rebase?** Check if `balanceOf` can change without a `Transfer` event. If yes, use share-based accounting.
3. **Does the token call back during transfer?** ERC-777 and ERC-1155 tokens trigger recipient callbacks, creating reentrancy vectors (see Ch9).
4. **Can the token be paused?** If the token's admin can freeze transfers, your protocol depends on that admin.
5. **Can the token be upgraded?** Proxy-based tokens can change their implementation arbitrarily.
6. **Does the Permit signature include a nonce?** Without it, every signature is replayable within the deadline window.

---

## Connection to Other Chapters

- **Ch4 (Flash Loans)**: The Warp Finance attack used a flash loan to manipulate the LP token valuation. Token economics vulnerabilities are amplified by the zero-capital nature of flash loans.
- **Ch9 (Reentrancy)**: Fee-on-transfer and rebase tokens often implement callbacks during transfer (ERC-777 pattern), creating a reentrancy vector that combines token economics with reentrancy.
- **Ch5 (Oracle Manipulation)**: LP token valuation is an oracle problem. The Warp Finance formula was mathematically correct but used manipulable inputs—the same class of error as spot price oracles.

---

## The Core Principle

Every protocol that accepts external tokens must answer one question: **what happens if the token does not behave like a standard ERC-20?**

The ERC-20 standard defines an interface—a set of function signatures. It does not define behavior. A token can implement `transfer()` to take a fee, trigger a callback, modify unrelated state, or simply return `false` without reverting. Every one of these behaviors breaks the assumptions that most DeFi protocols make about tokens.

The only safe approach is to treat every external token as potentially hostile. Measure received amounts rather than trusting stated amounts. Use share-based accounting rather than caching absolute balances. Verify the token's behavior with a test transaction before integrating it into production flows.

Tokens are the foundation of DeFi. If your assumptions about tokens are wrong, every calculation built on those assumptions is wrong. Warp Finance learned this lesson for $7.8 million. The question is whether your protocol will learn it before or after deployment.

---

*Next: Chapter 8 — Cross-Chain Vulnerabilities*
