# CodeHawks Audit Report — Thunder Loan

**Contest**: First Flight #3: Thunder Loan  
**Auditor**: Shiqiang Chen  
**Date**: July 16, 2026  
**Commit**: e8ce05f5530ca965165d41547b289604f873fdf6

---

## Finding Summary

| ID | Title | Severity | Status |
|:--:|------|:--:|:--:|
| [H-1] | Flash Loan Price Oracle Manipulation via TSwap Pool | 🔴 HIGH | Open |
| [M-1] | Storage Collision in ThunderLoan → ThunderLoanUpgraded | 🟡 MEDIUM | Open |
| [L-1] | `deposit()` CEI Pattern Deviation | 🔵 LOW | Open |

---

## [H-1] Flash Loan Price Oracle Manipulation via TSwap Pool

### Description

The `OracleUpgradeable.getPriceInWeth()` function retrieves token prices from a TSwap AMM pool using `getPriceOfOnePoolTokenInWeth()`. This is an instantaneous price query that can be manipulated within a single transaction via flash loans.

```solidity
// OracleUpgradeable.sol:19-22
function getPriceInWeth(address token) public view returns (uint256) {
    address swapPoolOfToken = IPoolFactory(s_poolFactory).getPool(token);
    return ITSwapPool(swapPoolOfToken).getPriceOfOnePoolTokenInWeth();
}
```

This price is consumed by `getCalculatedFee()` in both `ThunderLoan` and `ThunderLoanUpgraded`:

```solidity
// ThunderLoan.sol:246-251 / ThunderLoanUpgraded.sol:244-249
function getCalculatedFee(IERC20 token, uint256 amount) public view returns (uint256 fee) {
    uint256 valueOfBorrowedToken = (amount * getPriceInWeth(address(token))) / FEE_PRECISION;
    fee = (valueOfBorrowedToken * s_flashLoanFee) / FEE_PRECISION;
}
```

The fee is then applied to the exchange rate via `AssetToken.updateExchangeRate(fee)`, permanently distorting the share/asset ratio.

### Impact

An attacker can:
1. Take a flash loan of WETH
2. Swap WETH for the target token in the TSwap pool, inflating the token's price
3. Call `deposit()` — the manipulated price causes `getCalculatedFee()` to return an inflated fee
4. `updateExchangeRate()` pushes the exchange rate to a distorted value
5. Call `redeem()` to extract more underlying tokens than deposited
6. Repay the flash loan, keeping the profit

This is a variant of the **bZx (2020, $50M)** and **Harvest Finance (2020, $25M)** attacks — classified as **Pattern #1** in our DeFi attack taxonomy.

### Proof of Concept

```solidity
function testOracleManipulation() public {
    // 1. Flash loan WETH
    uint256 flashAmount = 1000e18;
    
    // 2. Manipulate TSwap pool
    tswapPool.swapExactInput(flashAmount, MIN_OUT, address(this));
    // Token price is now inflated
    
    // 3. Deposit — fee calculated at inflated price
    uint256 inflatedFee = thunderLoan.getCalculatedFee(token, 100e18);
    // inflatedFee >> normalFee
    
    // 4. Exchange rate permanently distorted
    thunderLoan.deposit(token, 100e18);
    
    // 5. Profit
    uint256 newRate = assetToken.getExchangeRate();
    assertGt(newRate, oldRate * 2); // Rate > 2x normal
}
```

### Tools Used

- Manual code review
- 50-Pattern DeFi Attack Taxonomy (Pattern #1)
- Foundry (line 193 comment: `slither-disable-next-line reentrancy-vulnerabilities` indicates developer awareness)

### Recommended Mitigation

Replace TSwap pool's `getPriceOfOnePoolTokenInWeth()` with a TWAP oracle:

```solidity
function getPriceInWeth(address token) public view returns (uint256) {
    // Use TWAP instead of instantaneous price
    return ITSwapPool(swapPoolOfToken).getPriceOfOnePoolTokenInWeth();
    // ⬆ Replace this with:
    // return ITSwapPool(swapPoolOfToken).consult(token, 1e18);
    // Where `consult()` returns the TWAP over N blocks
}
```

Or use Chainlink price feeds: `AggregatorV3Interface(priceFeed).latestRoundData()`

---

## [M-1] Storage Collision in ThunderLoan → ThunderLoanUpgraded

### Description

The `ThunderLoan` and `ThunderLoanUpgraded` contracts share the same inheritance chain and storage layout, but the upgraded version removes `s_feePrecision` while keeping `FEE_PRECISION` as a constant. If deployed as a UUPS upgrade, the `s_feePrecision` storage slot from the original contract becomes an uninitialized gap.

### Impact

Storage collision between old `s_feePrecision` and new storage layout could corrupt state during upgrade.

### Recommended Mitigation

Add a storage gap in `ThunderLoan` before upgrading:

```solidity
uint256[50] private __gap;
```

---

## [L-1] `deposit()` CEI Pattern Deviation (ThunderLoan only)

### Description

In `ThunderLoan.sol:147-156`, the `deposit()` function calls `token.safeTransferFrom()` AFTER calling `assetToken.mint()` and `assetToken.updateExchangeRate()`. While not directly exploitable (ERC-20 transfers don't trigger callbacks), this deviates from the Checks-Effects-Interactions pattern.

Note: `ThunderLoanUpgraded.sol:146-154` has improved this by calling `safeTransferFrom` immediately after `mint`, but still before the exchange rate update.

### Recommended Mitigation

Reorder to follow CEI strictly:
1. Effects: `mint` + `updateExchangeRate`
2. Interactions: `safeTransferFrom`
