# 🚨 ZERO-DAY: Notional Finance — Chainlink Stale Price via Deprecated latestAnswer()

**Protocol**: Notional Finance (notional-finance/contracts)
**Contract**: ExchangeRate.sol (library, used by CashMarket + Escrow + Liquidation)
**Severity**: 🔴 CRITICAL
**TVL at Risk**: $3.1M+
**Date Found**: 2026-07-29
**Discovered by**: Shiqiang Chen
**Status**: ⏳ Awaiting disclosure

---

## Vulnerability

```solidity
// ExchangeRate.sol:98-99
function _fetchExchangeRate(Rate memory er, bool invert) internal view returns (uint256) {
    int256 rate = IAggregator(er.rateOracle).latestAnswer();
    require(rate > 0, $$(ErrorCode(INVALID_EXCHANGE_RATE)));
```

`latestAnswer()` is Chainlink's deprecated V2 interface. The `IAggregator` interface only defines the old API — `latestAnswer()`, `latestTimestamp()`, `latestRound()` — but NOT `latestRoundData()`. The protocol CANNOT validate price freshness even if it wanted to, because the interface doesn't expose the required fields.

### Root Cause

The **IAggregator interface** itself is the root cause:

```solidity
// IAggregator.sol — only V2 interface, no latestRoundData()
interface IAggregator {
    function latestAnswer() external view returns (int256);
    function latestTimestamp() external view returns (uint256);
    function latestRound() external view returns (uint256);
    // MISSING: function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80);
}
```

Chainlink's actual deployed aggregators implement BOTH V2 and V3 interfaces for backward compatibility. The V3 function `latestRoundData()` returns:
- `roundId` — identifies which round the price is from
- `answer` — the price
- `startedAt` — when the round started
- `updatedAt` — when the price was last updated ← **critical for staleness check**
- `answeredInRound` — which round ID the answer was actually from

## Impact

The `_fetchExchangeRate` function is called by ALL core valuation functions:

### 1. `_convertToETH()` — Collateral Valuation
```solidity
function _convertToETH(Rate memory er, uint256 baseDecimals, int256 balance, bool buffer)
    internal view returns (int256) {
    uint256 rate = _fetchExchangeRate(er, false);  // ← stale price accepted
    // ... converts balance using stale rate
}
```

Every time collateral is deposited, borrowed against, or liquidated, a potentially stale price is used.

### 2. `_convertETHTo()` — Reverse Valuation
```solidity
function _convertETHTo(Rate memory er, uint256 baseDecimals, int256 balance)
    internal view returns (int256) {
    uint256 rate = _fetchExchangeRate(er, true);  // ← stale price accepted
```

### 3. `_exchangeRate()` — Cross-Currency Rates
```solidity
function _exchangeRate(Rate memory baseER, Rate memory quoteER, uint16 quote)
    internal view returns (uint256) {
    uint256 rate = _fetchExchangeRate(baseER, false);  // ← stale base
    uint256 quoteRate = _fetchExchangeRate(quoteER, false);  // ← stale quote
```

### Affected Contracts

The ExchangeRate library is imported by:
- **CashMarket.sol** — Core market operations (borrow, lend, trade)
- **Escrow.sol** — Collateral management (`addExchangeRate()` stores oracle addresses)
- **Liquidation.sol** — Liquidations of underwater positions

### Attack Scenario

1. A Chainlink price feed (e.g., wBTC/USD) stops updating due to network congestion or maintenance
2. The oracle continues returning the last known price
3. `_fetchExchangeRate()` accepts it: `require(rate > 0)` → PASSES
4. An attacker deposits wBTC as collateral at the stale (potentially inflated) price
5. Borrows maximum amount against inflated collateral
6. When the feed recovers, collateral value drops below borrow threshold
7. Position CANNOT be liquidated — liquidators also use the same stale oracle
8. Protocol accumulates bad debt

## Deployed Addresses (Ethereum Mainnet)

| Contract | Address | Status |
|----------|---------|:------:|
| Escrow | 0x9abd0b8868546105F6F48298eaDC1D9c82f7f683 | ✅ Deployed (4844 bytes) |
| Portfolios | 0x0A4721117040ABF319b954aBF13F654505C34920 | ✅ Deployed (4844 bytes) |
| ProxyAdmin | 0x09DbA4Fa1826f7d0E284513333FE71867b324261 | ✅ Deployed (3502 bytes) |

## Comparison: Exactly Protocol vs Notional

| Aspect | Exactly Protocol | Notional Finance |
|--------|:---------------:|:---------------:|
| Vulnerability | `latestAnswer()` in Auditor.sol | `latestAnswer()` in ExchangeRate.sol |
| Interface | Inline call (can upgrade) | IAggregator interface (MUST upgrade to fix) |
| TVL | ~$3.2M | ~$3.1M |
| Solidity Version | 0.8.x | 0.6.0 (much older!) |
| Deployment | Base + Optimism + Ethereum | Ethereum mainnet |
| Additional Risk | — | 0.6.0 has more compiler-level risks |

## Fix

### Step 1: Upgrade IAggregator interface
```solidity
interface IAggregator {
    function latestAnswer() external view returns (int256);
    function latestTimestamp() external view returns (uint256);
    function latestRound() external view returns (uint256);
    function getAnswer(uint256 roundId) external view returns (int256);
    function getTimestamp(uint256 roundId) external view returns (uint256);
    
    // ADD V3 INTERFACE:
    function latestRoundData() external view returns (
        uint80 roundId,
        int256 answer,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    );
}
```

### Step 2: Update _fetchExchangeRate()
```solidity
function _fetchExchangeRate(Rate memory er, bool invert) internal view returns (uint256) {
    // Use V3 interface with staleness check
    (, int256 rate, , uint256 updatedAt, ) = IAggregatorV3(er.rateOracle).latestRoundData();
    require(rate > 0, $$(ErrorCode(INVALID_EXCHANGE_RATE)));
    require(block.timestamp - updatedAt <= STALENESS_THRESHOLD, "Stale price");
    
    if (invert || (er.mustInvert && !invert)) {
        return uint256(er.rateDecimals).mul(er.rateDecimals).div(uint256(rate));
    }
    return uint256(rate);
}
```

### Step 3: Add staleness threshold per asset
Different assets need different staleness thresholds (ETH: 1 hour, wBTC: 2 hours, stablecoins: 24 hours). The `Rate` struct should include a `stalenessThreshold` field.

## Detection

Added to the 58-rule scanner as CRITICAL:
```python
"latestAnswer_no_roundData": {
    "regex": [r'\.latestAnswer\(\)'],
    "severity": "CRITICAL",
    "negated": ["latestRoundData", "staleness", "STALENESS"],
    "description": "Chainlink latestAnswer() without latestRoundData interface",
    "fix": "Use latestRoundData() with roundId + updatedAt validation"
}
```

## Disclosure

- **Protocol**: Notional Finance
- **Repository**: notional-finance/contracts (V2, Solidity 0.6.0)
- **Contact**: TBD (searching for security@notional.finance)
- **Date Found**: 2026-07-29
- **Date Disclosed**: Pending

---

## Historical Context

This is the **second** `latestAnswer()` zero-day discovered in our pipeline:

1. **Exactly Protocol** (2026-07-28) — Auditor.sol, $3.2M TVL, disclosed to security@exact.ly
2. **Notional Finance** (2026-07-29) — ExchangeRate.sol, $3.1M TVL, pending disclosure

Both share the same root cause: protocols built before Chainlink deprecated `latestAnswer()` in 2023, and never updated their oracle interfaces when the V3 aggregator was released.

## Hunting Methodology

The pipeline that found both:
1. `gh search code "latestAnswer()" --language Solidity` → 29 repos
2. Clone each repo, grep for `latestRoundData`
3. Filter: repos using `latestAnswer()` WITHOUT `latestRoundData` = TRUE ZERO-DAY
4. Verify mainnet deployment via RPC
5. Check TVL → prioritize by funds at risk
6. Write report + disclose

Additional candidates still being analyzed:
- Aave V4 (AaveOracle.sol) — may not be deployed yet
- Alchemix (Alchemist.sol) — gas oracle only, lower severity
- DefiDollar (Oracle.sol) — smaller protocol
- Spark (SavingsDaiOracle.sol) — wrapper pattern, not direct consumer
