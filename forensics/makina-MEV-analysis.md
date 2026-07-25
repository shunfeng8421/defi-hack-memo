# MEV Bot Exploitation — The makina Counter-Attack

## Incident Summary

| Detail | Value |
|------|------|
| Victim | makina (MEV searcher bot) |
| Attacker | Unknown — reverse-engineered bot |
| Method | Flash loan callback exploitation |
| Loss | $5.1M (2,800 ETH) |
| Date | January 2026 |

## Attack Chain

```
makina Bot (normal):
  1. Listen mempool → 2. Find arbitrage → 3. Flash loan → 4. Execute → 5. Repay → 6. Profit

Attacker (counter-exploit):
  1. Study makina's bot transactions on Etherscan
  2. Reverse-engineer: bot uses onFlashLoan with NO initiator check
  3. Deploy bait contract that triggers bot's flash loan
  4. onFlashLoan callback fires → bot's funds drained
  5. Attacker profits $5.1M
```

## Root Cause

The `onFlashLoan` callback trusted any caller. The bot assumed only legitimate arbitrage opportunities would trigger it. The attacker proved otherwise.

## Prevention

```solidity
require(initiator == address(this), "External initiator rejected");
```

One line. One check. Prevents counter-exploitation.

## Connection to 66-Pattern Taxonomy

Pattern #37: MEV Bot Replay / Counter-Attack
