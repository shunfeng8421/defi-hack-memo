# Chapter 5: Oracle Manipulation

*"Every DeFi protocol has exactly one point that connects code to reality. Attackers aim there."*

---

## The Most Expensive Function Call

On November 19, 2021, the CREAM Finance protocol detected an anomaly. A single address had borrowed $130 million worth of tokens using positions that should not have been possible. The collateral ratio was wrong. The liquidation threshold was wrong. Everything was wrong.

The post-mortem revealed a devastating simplicity. CREAM used a price oracle that read the spot price of yUSD from a Curve pool. An attacker flash-loaned a massive amount of ETH, swapped it into the Curve pool, and watched the yUSD price — the single number that determined every collateral calculation in the protocol — swing by 70%.

One function call. One manipulated number. $130 million gone.

The oracle was not the vulnerability. The oracle was working exactly as designed. It reported the current price of yUSD on Curve. The fact that this price could be manipulated for the cost of a flash loan was not a bug in the oracle. It was a fundamental misunderstanding of what the oracle was reporting.

---

## What Is an Oracle?

In the context of DeFi, an oracle is any mechanism that brings data from outside the blockchain into a smart contract. This data is almost always a price — the exchange rate between two assets — but it can also be a timestamp, a random number, a weather measurement, or any other off-chain value.

The defining challenge of oracles is that they bridge an information asymmetry:

- **On-chain**: Everything is transparent, deterministic, and verifiable. You can read any state variable of any contract. You can replay any transaction. You can prove exactly what happened.
- **Off-chain**: Nothing is transparent. Prices come from centralized exchanges where order books are hidden. Timestamps come from miner-reported values. Weather data comes from sensors that nobody can verify.

The oracle's job is to translate off-chain uncertainty into on-chain certainty. Every oracle fails at this job in some edge case. The security researcher's job is to find those edge cases before the attacker does.

---

## Pattern #4: Uniswap V2 Spot Price as Oracle

**Severity**: CRITICAL
**Real cases**: PancakeBunny $120M, CREAM $130M, Harvest $34M, bEarn $11M, Value DeFi $7.4M

This is the most common oracle vulnerability in DeFi. It appears in different forms — `getReserves()`, `.balance`, `totalSupply` — but the root cause is always the same: **using an instantaneous measurement where a time-averaged measurement is required.**

### The Vulnerability

```solidity
// ❌ VULNERABLE: Instant spot price
function getPrice() public view returns (uint256) {
    (uint256 r0, uint256 r1,) = pair.getReserves();
    return r0 * PRECISION / r1;
}
```

The function returns the exact price *at this moment.* One swap changes the reserves. One swap changes the price. The function has no memory and no protection.

### The Fix: TWAP

```solidity
// ✅ SAFE: Time-Weighted Average Price (Uniswap V2)
contract TwapOracle {
    IUniswapV2Pair public pair;
    uint256 public price0CumulativeLast;
    uint32 public blockTimestampLast;
    uint256 public priceAverage;
    
    function update() external {
        uint256 price0Cumulative = pair.price0CumulativeLast();
        uint32 blockTimestamp = uint32(block.timestamp % 2**32);
        uint32 timeElapsed = blockTimestamp - blockTimestampLast;
        
        if (timeElapsed > 0) {
            priceAverage = (price0Cumulative - price0CumulativeLast) / timeElapsed;
            price0CumulativeLast = price0Cumulative;
            blockTimestampLast = blockTimestamp;
        }
    }
    
    function consult(address token, uint256 amount) external view returns (uint256) {
        return priceAverage * amount / PRECISION;
    }
}
```

TWAP works by accumulating the price over time. `price0CumulativeLast` is the sum of `price × time elapsed` for every second since the pool was created. Dividing the change in cumulative price by the elapsed time gives the average price over that period.

To manipulate a TWAP oracle, an attacker must keep the price manipulated for the *entire averaging window*. A flash loan that manipulates the price for a single block will barely affect the cumulative value if the averaging window is large enough.

---

## Pattern #5: Chainlink Stale Price

**Severity**: HIGH
**Real case**: Venus Protocol $11M

Chainlink is the dominant oracle solution in DeFi. Its price feeds are updated by a decentralized network of node operators, making them resistant to the single-source manipulation that affects Uniswap spot prices.

But Chainlink has a different failure mode: **staleness**.

### The Vulnerability

Chainlink price feeds do not update continuously. Under normal conditions, they update every few minutes. Under extreme market volatility, they can go hours or days without updating. A protocol that reads the latest price without checking *when* that price was reported is using data that may no longer reflect reality.

```solidity
// ❌ VULNERABLE: Price without timestamp check
function getPrice() public view returns (uint256) {
    (, int256 price,,,) = feed.latestRoundData();
    return uint256(price);
}
```

### The Attack

1. Market volatility causes the Chainlink oracle to stop updating (heartbeat threshold reached)
2. The last reported price is now hours old — the real market price has moved significantly
3. Attacker identifies the stale oracle and the protocol that depends on it
4. Attacker borrows against collateral valued at the stale (inflated) price
5. When the oracle updates, the collateral value drops → protocol has bad debt

Venus Protocol lost $11 million to this exact scenario in 2021. The XVS token price was reported as $147 by Chainlink while the actual market price had dropped to $100. Attackers borrowed against the stale valuation and were not liquidated because the protocol's own oracle agreed that the collateral was worth $147.

### The Fix

```solidity
// ✅ SAFE: Price with freshness verification
function getPrice() public view returns (uint256) {
    (, int256 price,, uint256 updatedAt,) = feed.latestRoundData();
    require(block.timestamp - updatedAt < 1 hours, "Stale price");
    require(price > 0, "Negative price");
    return uint256(price);
}
```

The staleness threshold must be calibrated to the asset's volatility. A stablecoin may tolerate a 6-hour threshold. A volatile governance token may need 30 minutes. The threshold should be shorter than the protocol's liquidation window — liquidations must use a price that is fresher than the time it takes to execute a liquidation.

---

## Pattern #6: TWAP Multi-Block Manipulation

**Severity**: HIGH

TWAP oracles are not immune to manipulation. They are *more expensive* to manipulate. An attacker who can control multiple consecutive blocks — through validator collusion, MEV-boost manipulation, or aggressive gas bidding — can move the TWAP over a short averaging window.

### The Attack

1. Attacker gains control of block N (validators, MEV relays, or multi-block bundles)
2. Block N: Execute a large swap → manipulate the spot price
3. Block N+1: Continue the manipulation
4. Block N+2: Protocol reads the TWAP — but the 3-block window now consists entirely of manipulated prices

The attack requires controlling multiple consecutive blocks, which is expensive on Ethereum but cheaper on chains with lower validator requirements.

### The Fix

Use a longer TWAP window. A 30-minute window makes the attack require 100+ consecutive blocks — economically infeasible on Ethereum.

```solidity
// ✅ SAFE: Long TWAP window
uint256 constant MINIMUM_TWAP_PERIOD = 30 minutes;
```

---

## Pattern #7: Self-Reported Oracle

**Severity**: CRITICAL

The most dangerous oracle is the one that trusts a single entity.

```solidity
// ❌ VULNERABLE: Anyone can set the price
function setPrice(uint256 _price) external {
    price = _price;
}
```

This pattern appears more often than you would expect. It is the oracle equivalent of leaving your front door unlocked. Anyone who can call `setPrice()` can set the value that determines every position's collateral ratio, liquidation threshold, and withdrawal limit.

Variants of this pattern include:
- **Keeper-reported**: A designated keeper submits off-chain prices. If the keeper is compromised or malicious, the protocol has no fallback.
- **Multi-sig administered**: A multi-sig can adjust oracle parameters. If the multi-sig is socially engineered, all positions are at risk.
- **Governance-controlled**: Governance can vote to change oracle sources. A flash-loan governance attack can redirect the oracle.

### The Fix

Never have a single point of trust for oracle data:

```solidity
// ✅ SAFE: Multi-source oracle with deviation bounds
function getPrice() public view returns (uint256) {
    uint256 chainlinkPrice = chainlinkFeed.latestAnswer();
    uint256 twapPrice = twapOracle.consult(token, amount);
    
    // Both must agree within 5%
    uint256 deviation = abs(int256(chainlinkPrice) - int256(twapPrice)) * 1e18 / chainlinkPrice;
    require(deviation < 5e16, "Oracle deviation too high");
    
    return chainlinkPrice;
}
```

---

## The Oracle Detector

The 58-pattern scanner includes four oracle-specific patterns:

| Pattern | Name | Regex | Keyword |
|:--:|------|------|------|
| 4 | Spot Price Oracle | `getReserves()`, `.balance` | `!TWAP`, `!cumulative` |
| 5 | Chainlink Stale | `latestRoundData()` | `!updatedAt`, `!staleness` |
| 6 | TWAP Manipulation | `cumulative`, `average` | `!UNISWAP_V3`, `!window` |
| 7 | Self-Reported | `function.*price.*external` | `!multisig`, `!timelock` |

The scanner's job is to flag functions that *look* like they return price data and *lack* the safety mechanisms that would make them reliable. Human review determines whether the flagged function is actually used as an oracle.

---

## The Oracle Security Checklist

Before trusting any oracle in your protocol, verify:

1. **Source diversity**: Is the price derived from multiple independent sources?
2. **Freshness protection**: Is there a committed-to maximum staleness?
3. **Manipulation cost**: What does it cost to move the reported price by 1%?
4. **Circuit breaker**: What happens if all oracles fail simultaneously?
5. **Fallback oracle**: Is there a secondary oracle source with independent failure modes?

If any of these five questions has no answer, the oracle is not ready for production.

---

## The Deeper Lesson

Oracles are not a solved problem. Every oracle design has failure modes. The choice is not between a secure oracle and an insecure oracle — it is between known failure modes and unknown failure modes.

The protocols that survive oracle attacks are not the ones with perfect oracles. They are the ones that have designed their systems to fail gracefully when the oracle is wrong. Circuit breakers halt trading when prices deviate beyond reasonable bounds. Withdrawal limits cap the damage from any single incorrect price. Multi-source oracles require multiple independent systems to be compromised simultaneously.

The hardening gradient applies here too. Large protocols invest in oracle resilience because they know they are the target. Small protocols deploy `getReserves()` and hope nobody notices.

Someone always notices.

---

*Next: Chapter 6 — Access Control Failures*
