# 2 New Live Exploit Findings — July 19 Morning Hunt

## 1. Truebit $25M — Bonding Curve Price Manipulation

- **Loss**: 8,540 ETH (~$25M)
- **Date**: January 2026
- **Chain**: Ethereum Mainnet
- **Pattern**: #1 Flash Loan + Oracle + Bonding Curve

### Root Cause

Truebit's token uses a bonding curve for buy/sell pricing: `getPurchasePrice(amount)` calculates price based on `reserve` and `THETA` parameters. The attacker repeatedly:
1. Buys TRU at a low price (small purchase → moves curve slightly)
2. Sells TRU back immediately (the curve's sell price is higher due to fresh supply)

This **bonding curve arbitrage** is enabled because `getPurchasePrice()` depends on manipulable on-chain state and there's no cooldown between buy and sell.

### Detection
✅ Scanner Pattern #1 (Flash Oracle) fires on `getPurchasePrice()` + `reserve()` pattern

---

## 2. makina $5.1M — Multi-Pool Flash Loan Manipulation

- **Loss**: ~$5.1M USDC
- **Date**: February 2026
- **Chain**: Ethereum Mainnet
- **Pattern**: #1 Flash Loan + #7 AMM Reserve (Multi-Pool)

### Attack Flow (6 Steps)

```
1. Flash loan 280M USDC
2. Spend 110M USDC → DUSD/USDC pool → DUSD price inflates
3. Manipulate MIM/3Crv pool via 280M CRV
4. DUSD becomes overvalued → attacker's DUSD holdings surge in USD value
5. Swap inflated DUSD + LP tokens → USDC profit
6. Swap MIM/3Crv → repay flash loan
```

### Interesting Twist

The attack was **front-run by a MEV bot** (0x935...). The real attacker (0x2f9...) didn't get the profit — the MEV bot copied their strategy and executed first. This demonstrates Vector #5 (Timing Window Attack) in action.

### Detection
✅ Scanner Pattern #1 + #7 both fire

---

**Today hunt: 2 finds | $30.1M | #10 + #11 in the series**
