# Chapter 16: DEX Concentrated Liquidity Attacks

*"Uniswap V3 made liquidity 4,000x more capital-efficient. It also created attack vectors that didn't exist in V2."*

---

## The V3 Paradigm Shift

In May 2021, Uniswap launched V3, introducing concentrated liquidity—the ability to provide liquidity within a specific price range rather than across the entire curve from zero to infinity. A liquidity provider (LP) who expected ETH to trade between $1,800 and $2,200 could concentrate their entire position within that range, earning fees on every trade that passed through.

The capital efficiency gain was enormous. V3 positions could earn the same fees as V2 positions with 1/4000th the capital deployed. By mid-2022, V3 had surpassed V2 in total value locked and trading volume.

But the same mechanism that made V3 efficient also made it exploitable. In V2, every liquidity position participated in every trade. Manipulating the price required moving the entire pool's reserves—a capital-intensive operation that was only profitable with flash loans. In V3, the attacker only needed to move the price outside a specific LP's concentrated range. A position with a 1% price width could be rendered inactive by a 1.1% price movement, requiring a fraction of the capital.

The lesson: **capital efficiency is security trade-off. The more concentrated the liquidity, the less capital required to manipulate it.**

---

## How V3 Tick Mechanics Work

Uniswap V3 divides the price space into discrete "ticks"—price points at which liquidity can be added or removed. When a swap crosses a tick boundary, liquidity from the next range activates and the pool's fee tier operates on the new liquidity profile.

The tick spacing creates a discontinuous price curve. Between ticks, the price follows a smooth function (the constant product formula). At tick boundaries, the price can jump as new liquidity sources enter or exit.

This discontinuity is the source of every V3-specific vulnerability:

1. **Tick manipulation**: An attacker can push the price across a tick boundary to change the liquidity profile mid-swap
2. **Range sandwiching**: An attacker can push the price OUTSIDE an LP's range, rendering their position inactive
3. **JIT liquidity**: An attacker can add liquidity at the exact tick range a large swap will traverse, then remove it immediately after

---

## Pattern #47: Just-In-Time Liquidity Extraction

**Severity**: HIGH

### The Attack

A large swap is visible in the mempool—100 ETH to be exchanged for USDC. A MEV searcher calculates the exact tick range this swap will traverse. In the same block, before the swap executes, the searcher:

1. **Adds** concentrated liquidity at the exact price range the swap will cross
2. The swap executes through the searcher's newly-added liquidity
3. The searcher **removes** the liquidity immediately after the swap processes

The searcher captures the swap fees without bearing any inventory risk. Their capital was deployed for a single transaction. Their only cost was gas.

The LP who had maintained the position for weeks—absorbing inventory risk, rebalancing their range with price movements, paying gas for each adjustment—earned nothing from this swap. The JIT provider extracted the fees that should have gone to the committed LP.

### The Fix

Minimum liquidity duration:

```solidity
mapping(bytes32 => uint256) public positionCreatedAt;

function addLiquidity(AddLiquidityParams calldata params) external returns (bytes32 positionId) {
    positionId = keccak256(abi.encode(msg.sender, params));
    positionCreatedAt[positionId] = block.timestamp;
    _addLiquidity(params);
}

function removeLiquidity(bytes32 positionId) external {
    require(
        block.timestamp >= positionCreatedAt[positionId] + 10 minutes,
        "Position held for less than minimum duration"
    );
    _removeLiquidity(positionId);
}
```

A 10-minute minimum holding period forces JIT providers to bear 10 minutes of inventory risk—enough to deter the strategy on all but the most volatile pairs. The committed LPs retain their fee advantage.

---

## Pattern #48: Tick Boundary Price Manipulation

**Severity**: HIGH

### The Attack

An attacker identifies a large LP position concentrated in a narrow tick range (e.g., ETH/USDC between ticks 1800 and 1820). The attacker:

1. Flash-loans a large amount of ETH
2. Swaps ETH for USDC, crossing the upper tick boundary (1820)
3. The LP's position is now out of range—their liquidity is inactive
4. The attacker executes their profitable trade with reduced slippage (less liquidity active)
5. Swaps USDC back to ETH, crossing the tick boundary in reverse
6. Repays the flash loan

The LP's liquidity was neutralized for the duration of the attack. The attacker profited from the reduced slippage.

### The Fix

TWAP oracles that query the geometric mean price across multiple ticks, smoothing the discontinuity:

```solidity
function getPrice() external view returns (uint256) {
    uint32[] memory secondsAgos = new uint32[](2);
    secondsAgos[0] = 1800;  // 30 minutes ago
    secondsAgos[1] = 0;      // now
    
    (int56[] memory tickCumulatives,) = pool.observe(secondsAgos);
    int56 tickDelta = tickCumulatives[1] - tickCumulatives[0];
    // TWAP across 30 minutes, not a single tick
}
```

A single tick can be manipulated in one block. A 30-minute TWAP requires sustained manipulation across ~150 blocks, which is economically prohibitive.

---

## Pattern #49: Fee Tier Arbitrage

**Severity**: MEDIUM

### The Attack

Uniswap V3 supports multiple fee tiers (0.01%, 0.05%, 0.3%, 1%) for the same token pair. An attacker can execute a multi-hop trade that exploits the fee differential:

1. Swap on the 0.01% pool to push the price
2. The 0.05% pool reads the new price from the 0.01% pool via the oracle
3. Arbitrage between the two pools captures the spread minus the 0.01% fee

The attack exploits the independence of fee-tier-specific pools—each pool maintains its own price, and the cross-pool oracle feed has inherent latency.

### The Fix

Cross-pool price validation before executing price-dependent operations. Any protocol that uses a V3 pool as an oracle must verify that the pool's price is consistent with the aggregate price across all fee tiers for that pair.

---

## The DEX Security Checklist

1. **TWAP oracles, not spot ticks, for all price-dependent operations.**
2. **Minimum liquidity duration prevents JIT extraction.** 10 minutes minimum.
3. **Slippage tolerance is explicitly set on every swap.** Never `type(uint256).max`.
4. **Cross-fee-tier price validation before oracle-dependent actions.**
5. **Flash-loan resistant pricing uses multi-block averaging.**

---

## Connection to Other Chapters

- **Ch4 (Flash Loans)**: Every V3 attack is amplified by flash loans. The capital to cross tick boundaries would otherwise be prohibitive.
- **Ch14 (MEV)**: JIT liquidity is MEV applied to the LP fee market. The same mempool visibility that enables sandwich attacks enables JIT extraction.
- **Ch5 (Oracle Manipulation)**: V3 tick manipulation is spot oracle manipulation in a new form. The fix (TWAP) is identical.

---

*Next: Chapter 17 — DePIN Physical-Layer Attacks*
