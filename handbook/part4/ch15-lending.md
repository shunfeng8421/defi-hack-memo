# Chapter 15: Lending Protocol Attacks

*"A loan is a promise. In DeFi, that promise is enforced by code that can be tricked."*

---

## The RadiantCapital Incident: January 2024

On January 2, 2024, RadiantCapital—a lending protocol on Arbitrum with over $300 million in total value locked—was exploited for $4.5 million. The attacker did not find a bug in Radiant's code. They exploited a feature that Radiant had inherited from Compound, the protocol it was forked from.

Compound's lending model uses a system of "collateral factors"—ratios that determine how much a user can borrow against their deposited assets. Depositing $100 of ETH with a 75% collateral factor allows borrowing $75 of USDC. The model also uses "enter markets"—a function that registers assets as collateral and links them for cross-collateral calculations.

The attacker noticed a subtle interaction: when a user entered a new market, the protocol recalculated all existing positions using the new market's parameters. By timing their market entry to coincide with a specific price oracle state, the attacker could borrow against collateral that should not have been eligible.

$4.5 million was borrowed against effectively worthless collateral. The loan was never repaid. The protocol's liquidation engine—designed to protect against under-collateralized loans—never triggered because the oracle manipulation happened in the same block and was invisible to the liquidation system by the time it processed.

---

## Why Lending Protocols Are Complex

Lending protocols are the most mathematically complex class of DeFi applications. A DEX has one job: facilitate a swap at a fair price. A lending protocol has multiple interacting systems:

1. **Deposit accounting**: tracking who deposited what, and how much they are owed
2. **Collateral management**: determining which assets can serve as collateral and at what ratios
3. **Borrow limits**: calculating maximum borrow amounts based on collateral value
4. **Interest rate models**: dynamic rates that respond to utilization
5. **Liquidation**: a competitive auction system that closes under-collateralized positions
6. **Oracle integration**: price feeds for every supported asset

Each system is individually complex. Their interactions are combinatorially complex. The most dangerous lending protocol vulnerabilities are not in any single system—they are in the boundaries where two systems interact.

---

## Pattern #38: Bad Debt Accumulation

**Severity**: HIGH
**Real cases**: RadiantCapital $4.5M, Moonwell $1.78M

### The Vulnerability

A lending protocol's liquidation engine cannot liquidate positions fast enough, or cannot liquidate them at all. Under-collateralized positions accumulate as bad debt on the protocol's balance sheet.

```solidity
// ❌ VULNERABLE: No incentive for timely liquidation
function liquidate(address borrower) external {
    require(isUnderCollateralized(borrower), "Position healthy");
    // Liquidator receives fixed bonus
    // If gas cost > bonus, no one liquidates
}
```

### The Attack

The attacker creates a position that will become under-collateralized when the oracle price moves. The price moves. The position is now under water. But the liquidation bonus is too small to attract liquidators, or the collateral is too illiquid to sell on a DEX. The position remains open. The protocol is owed money it will never recover.

This is not a flash-loan attack. It is a slow bleed that compounds over time as more positions become unhealthy and no liquidators step in.

### The Fix

Dynamic liquidation incentives:

```solidity
function getLiquidationBonus(address borrower) public view returns (uint256) {
    uint256 healthFactor = getHealthFactor(borrower);
    if (healthFactor < 0.5e18) return 20e16;  // 20% bonus for severely underwater
    if (healthFactor < 0.8e18) return 10e16;  // 10% bonus for moderately underwater
    return 5e16;  // 5% base bonus
}
```

The more underwater a position is, the higher the liquidation bonus. This ensures liquidators are always incentivized to close the worst positions first.

---

## Pattern #39: Liquidation Front-Running

**Severity**: HIGH

### The Vulnerability

A pending liquidation transaction is visible in the mempool. A MEV searcher copies the liquidation call, increases the gas price, and executes it first. The original liquidator's transaction fails.

This creates a "liquidation lottery" where only the fastest bots can capture liquidation profits. Worse, it discourages honest liquidators from participating, which means positions stay underwater longer.

### The Fix

Dutch auction liquidations:

```solidity
function liquidate(address borrower) external returns (uint256) {
    uint256 discount = getCurrentDiscount(borrower);  // Starts at 1%, increases over time
    // Liquidator receives collateral at discount
    // Early liquidation = smaller discount = competition
    // Late liquidation = larger discount = guaranteed profit
}
```

The discount increases over time. The first liquidator to act gets a small discount. If nobody acts quickly, the discount grows until someone steps in. This eliminates the front-running incentive because there is no fixed "first mover advantage."

---

## Pattern #40: Non-Liquidatable Collateral

**Severity**: HIGH

### The Vulnerability

A user deposits collateral that cannot be liquidated. Either the collateral token has no liquid market on any DEX, or the token has transfer restrictions that prevent the protocol from selling it.

```solidity
function addCollateral(address token, uint256 collateralFactor) external onlyAdmin {
    // ❌ No liquidity check
    supportedCollateral.push(token);
    collateralFactors[token] = collateralFactor;
}
```

### The Attack

1. Attacker identifies a token with a high collateral factor but low DEX liquidity
2. Attacker deposits a large amount of this token as collateral
3. Attacker borrows against the inflated collateral value
4. When the position becomes under-collateralized, the protocol tries to liquidate
5. The DEX has no liquidity to absorb the collateral sale → liquidation fails
6. The protocol is stuck with bad debt

### The Fix

Every collateral asset must pass a liquidity test:

```solidity
function addCollateral(address token, uint256 collateralFactor) external onlyGovernance {
    uint256 liquidity = getDexLiquidity(token);
    require(liquidity >= minLiquidityThreshold, "Insufficient liquidity");
    supportedCollateral.push(token);
}
```

---

## Pattern #41: Rounding Exploit in Health Factor

**Severity**: MEDIUM
**Real case**: Hundred Finance $7.4M

### The Vulnerability

The health factor—which determines if a position is liquidatable—is calculated using integer arithmetic. Rounding errors can make an underwater position appear healthy.

```solidity
function getHealthFactor(address user) public view returns (uint256) {
    uint256 collateralValue = getCollateralValue(user);
    uint256 borrowValue = getBorrowValue(user);
    return collateralValue * 1e18 / borrowValue;  // Integer division!
}
```

If `collateralValue = 100` and `borrowValue = 101`, the health factor is `100 * 1e18 / 101 ≈ 0.99e18`. The position is underwater but very close to the threshold. A rounding error in either direction can determine whether the position is liquidatable.

### The Fix

Always round against the user:

```solidity
function getHealthFactor(address user) public view returns (uint256) {
    uint256 collateralValue = getCollateralValue(user);
    uint256 borrowValue = getBorrowValue(user);
    // Round down for collateral, round up for borrow
    return collateralValue * 1e18 / borrowValue;  // Rounds down = pessimistic
}
```

---

## The Lending Protocol Checklist

1. **Liquidation bonuses are dynamic and sufficient to attract liquidators.** If gas > bonus, no one will liquidate.
2. **Collateral assets have verified DEX liquidity.** No market = no liquidation.
3. **Health factors round against the user in all calculations.** Never give the benefit of rounding to the borrower.
4. **Oracle prices for collateral and borrow assets are independent.** Never use the same oracle for both sides of a position.
5. **Entering/exiting markets triggers recalculation of all dependent positions.** And that recalculation is done atomically to prevent inter-block manipulation.

---

## Connection to Other Chapters

- **Ch4 (Flash Loans)**: The RadiantCapital attack used flash-loaned collateral to amplify the borrow. Lending protocol vulnerabilities are force-multiplied by flash loans.
- **Ch5 (Oracle Manipulation)**: Liquidation is triggered by oracle prices. Oracle manipulation creates false liquidation events.
- **Ch14 (MEV)**: Liquidation front-running is a specialized form of MEV. The same mempool visibility that enables sandwich attacks enables liquidation theft.

---

*Next: Chapter 16 — DEX Concentrated Liquidity Attacks*
