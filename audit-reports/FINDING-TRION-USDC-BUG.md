# 🚨 0-Day Finding: TRIONCrowdfundVault — USDC Conversion Precision Bug

**Protocol**: TRION Protocol Crowdfund (dev-analyshd/trion-protocol-crowdfund)
**Date Found**: 2026-07-25
**Severity**: HIGH

## Vulnerability

Line 96 of `TRIONCrowdfundVault.sol`:

```solidity
uint256 ethEquivalent = (amount * 1 ether) / 2000 * 1e6;
```

Due to Solidity's left-to-right operator precedence and the misplaced `* 1e6`, this formula inflates the ETH equivalent by a factor of ~10^12.

## Impact

| USDC Amount | Reported ETH Equivalent | Actual |
|--:|--:|--:|
| 1 USDC | 500,000,000 ETH | 0.0005 ETH |
| 100 USDC | 50,000,000,000 ETH | 0.05 ETH |

**Result**: ANY contribution ≥ 1 USDC instantly achieves Gold tier (150,000 TRIO tokens allocated).

## Root Cause

The `* 1e6` multiplication is applied AFTER the division, canceling the conversion scale. The intended formula was:

```solidity
// ❌ Buggy
(amount * 1 ether) / 2000 * 1e6

// ✅ Correct
(amount * 1 ether) / (2000 * 1e6)
```

## Fix

Add parentheses to ensure correct order of operations:

```solidity
uint256 ethEquivalent = (amount * 1 ether) / (2000 * 1e6);
```

## Status

- [x] Found
- [ ] Reported to dev-analyshd
- [ ] Fix confirmed
