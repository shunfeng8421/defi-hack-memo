# DxSale $7.3M — Systematic Backdoor (March 2026)

- **Loss**: $7.3M USD | **Pattern**: #50 — Intentional Backdoor

## Root Cause

DxSale locker ownership transferred through **89 wallets over 269 days**. Each transfer was small enough to avoid detection. After accumulating control, the attacker unlocked and drained all locked liquidity.

## Why It Matters

This is NOT a code bug — it's a premeditated fraud baked into the protocol from day 1. The deployer built the transfer mechanism knowing they would exploit it later. **Our scanner cannot detect this** — it requires forensic analysis of transaction patterns.

## Detection Suggestion

Monitor for: ownership transfers through >5 wallets within 12 months. Flag as "potential backdoor."

---

# VerusBridge $11.58M — ZK Bridge Exploit (May 2026)

- **Loss**: $11.58M | **Chain**: Verus | **Pattern**: Cross-Chain + ZK Proof

## Root Cause

VerusBridge's ZK proof verification allowed **spoofed Merkle proofs** to pass validation, enabling the attacker to mint tokens on the destination chain without a corresponding lock on the source chain.

## Why It Matters

Cross-chain ZK bridges are the NEWEST attack surface. Our scanner flags "Cross-Chain Replay" but ZK proof spoofing is undetectable by static analysis.

---

# futureswap $394K — Fee Precision Error (Jan 2026)

- **Loss**: $394K USDC + 67 WETH | **Pattern**: #34 — Division Before Multiply

## Root Cause

`feeRateWad` interpreted as **basis points** instead of **wad** (1e18):
```solidity
// BUG: feeRateWad = 30 → interpreted as 30 bps (0.3%) instead of 30/1e18
uint256 fee = amount * feeRateWad / 10000; // ❌ precision error
// Correct: fee = amount * feeRateWad / 1e18;
```
This 10000x multiplication error caused the fee to be calculated as a 30% rate instead of 0.3%.

## Detection

Our scanner's Pattern #34 (Division Before Multiplication) flags this exact type of precision error.
