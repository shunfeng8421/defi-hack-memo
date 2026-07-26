# BettingEngine Security Audit — Agent Prediction Markets

**Contract**: BettingEngine.sol (453 lines)
**Severity**: 1 CRITICAL, 3 HIGH

---

## 🔴 CRITICAL: Assembly-Based Winning Outcome Extraction (Line 254-257)

```solidity
uint256 winningOutcome;
assembly {
    winningOutcome := mload(add(data, 320)) // Approximate offset
}
```

The comment says "Approximate offset." This is **not approximate** — it is **arbitrary**. The function calls `marketFactory.markets(marketId)` via a raw call, then reads 320 bytes into the returned data without ANY knowledge of the actual struct layout.

**Exploitation**: If the MarketFactory struct changes — or even if Solidity's ABI encoder adds padding — the assembly reads garbage memory. Every bet settlement becomes a coin flip: the attacker bets on all outcomes and claims the one whose garbage-read happens to match.

**Fix**: Use proper ABI decoding:
```solidity
(, , , , , , , , , , uint256 winningOutcome, ) = 
    IMarketFactory(marketFactory).markets(marketId);
```

Or better: store `winningOutcome` in `BettingEngine` during `resolveMarket()` instead of re-querying `marketFactory` during every claim.

---

## 🟠 HIGH: Winning Outcome Must Be Re-Queried on Every Claim (Line 248-257)

`claimWinnings()` makes an external call to `marketFactory` to get the winning outcome. Every single claim triggers this call. If `marketFactory` is compromised or upgraded to a malicious implementation, the winning outcome can change between two users' claims.

**Fix**: Store `winningOutcome` in `resolveMarket()`. Never re-query after resolution.

---

## 🟠 HIGH: First Bet Always 2x (Line 427-429)

```solidity
if (currentLiquidity == 0) {
    return betAmount * 2; // First bet gets 2x
}
```

The first bettor on any outcome gets guaranteed 2x. Combined with `adminResolve()` (OracleResolver CRITICAL #1), the owner can:
1. Place first bet on their chosen outcome → gets 2x
2. Call `adminResolve()` → marks their outcome as winner
3. Claim guaranteed 2x payout

**Fix**: First bet should get the same odds calculation, not a guaranteed multiplier.

---

## 🟡 MEDIUM: No Payout Cap Per Market

The contract has `MAX_SLIPPAGE_BPS` but no maximum on total payout per market. If a market accumulates large positions on a single outcome, the total payout can exceed the contract's ETH balance — making the contract insolvent.

**Fix**: Track total potential payout per market. Reject bets that would exceed `address(this).balance`.

---

## Verdict: 3.5/10

The assembly-based memory read (CRITICAL) makes the entire payout system unreliable. Combined with the OracleResolver's `adminResolve` backdoor, the protocol's security model is owner-dependent through two independent channels — oracle control and memory corruption.
