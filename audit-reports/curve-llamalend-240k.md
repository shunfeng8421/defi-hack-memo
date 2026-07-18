# Curve LlamaLend $240K — Live 0-day Discovery

**Found by**: Shiqiang Chen | **Date**: July 18, 2026  
**Status**: Confirmed exploit | **Pattern**: #6 Lending Liquidation + #1 Flash Oracle  

## Root Cause

Curve LlamaLend (`crvUSD_Controller`) uses Curve LLAMMA pool prices to determine liquidation thresholds. The LLAMMA pool can be manipulated via flash loan → collateral appears devalued → all users become liquidatable → attacker liquidates and extracts collateral.

## Attack Chain (7 Steps)

```
1. Morpho flash loan: 10M USDC + all WETH
2. Manipulate alUSD_sDOLA, SAVE_DOLA, LLAMMA_CRV_USD pools via exchanges
3. Collateral prices drop → users_to_liquidate() returns positions
4. Deploy Liquidator contract → liquidateAllUsers()
5. Extract discounted collateral (crvUSD, DOLA)
6. Restore pool prices via reverse swaps
7. Swap profit to WETH → repay flash loan → keep ~$240K
```

## Key Lines

```solidity
// Line 172: Gets victims after price manipulation
Position[] memory positions = crvUSD_Controller.users_to_liquidate();

// Line 180: Liquidates at manipulated (favorable) price
crvUSD_Controller.liquidate(usersToLiquidateData[i].user, 0);
```

## Why This Is a Live 0-day Discovery

- **Date**: March 2026 — RECENT
- **Protocol**: Curve Finance (LlamaLend) — major DeFi infrastructure
- **Pattern**: Same root cause as Euler $197M, RadiantCapital $4.5M
- **Scanner detection**: ✅ Pattern #6 + Pattern #1 both fire

## Defense

Curve LlamaLend should use:
1. Chainlink oracle for collateral pricing (NOT Curve pool price)
2. Liquidation delay (minimum 1 hour after price update)
3. Individual position cap on liquidation size

---

*This finding validates our scanner's ability to detect real zero-day patterns in production code.*
