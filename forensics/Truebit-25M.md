# On-Chain Forensics: Truebit $25M
## Bonding Curve Attack — No Cooldown, No Defense

**Date**: July 2026  
**Amount**: 8,540 ETH (~$25M)  
**Protocol**: Truebit — verification game for off-chain computation  
**Root Cause**: Bonding curve buy/sell had zero cooldown between operations

---

## Attack Flow

```
┌──────────────────────────────────────────────┐
│ Truebit Token Economics                       │
│                                               │
│ BUY:  send ETH → mint TRU tokens              │
│       Price INCREASES with supply (bonding)   │
│ SELL: burn TRU tokens → receive ETH           │
│       Price DECREASES with supply (bonding)   │
│                                               │
│ Key: No cooldown between buy and sell         │
├──────────────────────────────────────────────┤
│ Step 1: Exploit bonding curve mathematics     │
│ Calculate: buy price at N, sell price at N+K  │
│ Find K where profit > gas                     │
├──────────────────────────────────────────────┤
│ Step 2: Execute millisecond-speed loop        │
│ BUY  → price rises                            │
│ SELL → price falls (but still above entry)    │
│       because the curve is asymmetric          │
│                                               │
│ Repeat 1000s of times in one transaction      │
├──────────────────────────────────────────────┤
│ Step 3: Extract 8,540 ETH                     │
│ Each cycle: tiny profit                       │
│ 1,000 cycles/sec × gas optimization = $25M    │
└──────────────────────────────────────────────┘
```

## The Vulnerability

The bonding curve formula created an exploitable asymmetry:
- Buy price = f(N) where N = current supply
- Sell price = f(N+K) where K = new tokens minted
- If f(N+K) > f(N) * fee, each buy→sell cycle is profitable

The absence of a cooldown allowed thousands of cycles in a single transaction.

## Fix

```solidity
// Minimum 1-hour cooldown between buy and sell
mapping(address => uint256) public lastBuyAt;
uint256 constant COOLDOWN = 1 hours;

function sell(uint256 amount) external {
    require(block.timestamp >= lastBuyAt[msg.sender] + COOLDOWN,
        "Cooldown not expired");
    // ... execute sell
}
```

## Pattern

Pattern #46: Bonding Curve Manipulation — Unbounded loop with no rate limiting.
