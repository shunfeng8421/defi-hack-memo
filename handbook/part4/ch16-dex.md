# Chapter 16: DEX Concentrated Liquidity Attacks

*"Uniswap V3 made liquidity 4,000x more capital-efficient. It also made it 4,000x more exploitable."*

---

## The V3 Revolution and Its Attack Surface

Uniswap V3 introduced concentrated liquidity: liquidity providers can deploy capital within a specific price range rather than across the entire price curve from zero to infinity. A LP who believes ETH will trade between $1,800 and $2,200 can concentrate their entire position within that range, earning fees on every trade that passes through.

This is dramatically more capital-efficient than V2's uniform distribution. It is also dramatically more vulnerable to targeted manipulation.

In V2, manipulating the price required moving the entire pool's reserves—a capital-intensive operation that was only profitable with flash loans. In V3, the attacker only needs to move the price outside the LP's concentrated range. A position with a 1% price range can be rendered inactive by a 1.1% price movement, which requires a fraction of the capital.

---

## Pattern #42: Tick Boundary Manipulation

**Severity**: HIGH

### The Attack

Uniswap V3 prices move in discrete "ticks"—price points at which liquidity can be added or removed. When a swap crosses a tick boundary, the pool's fee tier changes and liquidity from the next range activates.

An attacker can:
1. Flash-loan a large amount of the base token
2. Swap across a tick boundary → activate liquidity in the next range
3. Execute their profitable trade at the new tick's pricing
4. Swap back, crossing the tick boundary in reverse

The attack exploits the discrete nature of V3's price curve. The continuous price of V2 could be manipulated incrementally. V3's price jumps at tick boundaries, creating deterministic profit opportunities.

### The Fix

TWAP oracles that query the geometric mean price across multiple ticks, rather than a single spot tick:

```solidity
function getPrice() external view returns (uint256) {
    return pool.observe(secondsAgos);  // Multi-tick TWAP, not single tick
}
```

---

## Pattern #43: Range Order Sandwich

**Severity**: HIGH

### The Attack

A LP places a concentrated position in a narrow range, expecting to capture fees from swaps through that range. A MEV searcher:

1. Sees the LP's position on-chain
2. Submits a swap that pushes the price OUTSIDE the LP's range
3. Submits another swap that pulls the price back INTO the range
4. Captures the fee that would have gone to the LP

The LP provided the liquidity. The MEV searcher captured the fee. This is the MEV version of "I did the work, you took the profit."

### The Fix

Minimum position duration (similar to JIT liquidity defense in Ch14):

```solidity
function removeLiquidity(uint256 tokenId) external {
    require(
        block.timestamp >= positionCreatedAt[tokenId] + MIN_DURATION,
        "Position too new"
    );
    _removeLiquidity(tokenId);
}
```

---

## Pattern #44: Fee Tier Arbitrage

**Severity**: MEDIUM

### The Attack

Uniswap V3 offers multiple fee tiers (0.01%, 0.05%, 0.3%, 1%) for the same token pair. An attacker can:

1. Trade through the 0.01% fee pool to move the price
2. The 0.05% pool reads the price from the 0.01% pool
3. Arbitrage between the two pools, capturing the fee difference

The attack exploits the assumption that all pools for the same token pair should have the same price. Fee tier differences break this assumption temporarily.

---

## The DEX Checklist

1. **TWAP oracles, not spot ticks, for all price-dependent operations.**
2. **Minimum position duration prevents JIT liquidity extraction.**
3. **Slippage tolerance explicitly set on every swap.**
4. **Multiple fee tiers require cross-tier price validation.**

---

*Next: Chapter 17 — DePIN Physical-Layer Attacks*
