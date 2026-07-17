# AztecConnect $2.19M — ZK Rollup Exploit (June 2026)

- **Protocol**: Aztec Connect (ZK Rollup)
- **Date**: June 14, 2026
- **Loss**: $2,190,000 (908 ETH + 270K DAI + 167 wstETH)
- **Pattern**: ZK Proof Verification Bypass

## Root Cause

The ZK rollup's `numRealTxs` parameter mismatched between proof commitment and L1 settlement:
- **Proof committed** to FULL inner-rollup chunks (all transactions)
- **Settlement processed** EXACTLY `numRealTxs` transactions
- When `numRealTxs` < total chunks: proof covers MORE than what's settled → unverified state transitions pass verification

## Detection

This is a **business logic** vulnerability — our scanner's keyword matching cannot detect ZK proof verification bypass. Requires manual understanding of rollup architecture.

Pattern: New — "ZK Proof Scope Mismatch"  
Scanner detection: ❌ (beyond static analysis)
