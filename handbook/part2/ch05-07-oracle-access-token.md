# Chapter 5-7: Oracle · Access · Token

## Chapter 5: Oracle Manipulation (Patterns 5-8)

### Pattern #5: ERC-4626 Vault Inflation

**Severity**: CRITICAL · **Real**: Multiple vaults drained

The first depositor can manipulate the share price to steal from later depositors. Deposit 1 wei + donate 100 ETH → share price = astronomical → rounding steals from everyone.

### Pattern #6: Uniswap V2 Spot as Oracle

**Severity**: CRITICAL · **Real**: PancakeBunny $120M

The most common oracle mistake. `getReserves()` returns instantaneous values. One swap changes them.

### Pattern #7: Chainlink Stale Price

**Severity**: HIGH · **Real**: Venus Protocol $11M

Chainlink may not update during high volatility. Always check `updatedAt`.

```solidity
(, int256 price,, uint256 updatedAt,) = feed.latestRoundData();
require(block.timestamp - updatedAt < 1 hours, "Stale");
```

### Pattern #8: Self-Reported Oracle

**Severity**: CRITICAL

Anyone can call `setPrice()`. No access control, no TWAP, no validation. Instant liquidation of all positions.

---

## Chapter 6: Access Control (Patterns 9-14)

### Pattern #12: Missing Access Control

**Severity**: HIGH · **Everywhere**

Public function that should be restricted. No `onlyOwner`, no `require(msg.sender == admin)`. Anyone can call it.

### Pattern #13: Admin Key Privilege Escalation

**Severity**: HIGH · **Real**: PolyNetwork $610M

Single admin key without timelock. Compromise one key → upgrade to malicious implementation → drain entire protocol.

**Fix**: Timelock + multi-sig. Minimum 48-hour delay on any upgrade.

---

## Chapter 7: Token Economics (Patterns 15-18)

### Pattern #15: Permit Without Nonce

**Severity**: MEDIUM

`permit(owner, spender, value, deadline, v, r, s)` without nonce. Signature is valid forever within the deadline window. Front-run in mempool.

### Pattern #16: Deflationary Token Attack

**Severity**: HIGH

Token has transfer fee → contract receives less than expected → but credits full amount → protocol loses money on every transaction.

### Pattern #17: Mint/Burn Asymmetry

**Severity**: MEDIUM

`mint()` and `burn()` use different accounting formulas. Over time, `totalSupply` drifts away from the sum of all balances. Either creates tokens from nothing or destroys them.

---

## Quick Reference: Patterns 1-18

| # | Pattern | Severity |
|:--:|------|:--:|
| 1 | Spot Price Oracle | 🔴 |
| 2 | CEI/Reentrancy | 🔴 |
| 3 | Flash+Reentrancy | 🔴 |
| 4 | TWAP Multi-Block | 🟠 |
| 5 | ERC-4626 Inflation | 🔴 |
| 6 | Uniswap V2 Oracle | 🔴 |
| 7 | Chainlink Stale | 🟠 |
| 8 | Self-Reported Oracle | 🔴 |
| 12 | Missing Access | 🟠 |
| 13 | Admin Key | 🟠 |
| 15 | Permit Front-run | 🟡 |
| 16 | Deflation Attack | 🟠 |
| 17 | Mint/Burn Drift | 🟡 |

---

*Next: Chapter 8 — Cross-Chain Vulnerabilities*
