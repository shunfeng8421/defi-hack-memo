# Full DeFiHackLabs Scan Report — 58-Pattern Scanner

**Date**: 2026-07-23 | **Scanner**: v2.0 (50 DeFi + 8 Solana)

## Summary

| Metric | Value |
|------|--:|
| Files Scanned | 200+ (2017-2026) |
| Total Lines | 90,000+ |
| Total Findings | 3,000+ |
| Pattern Types Hit | 35/58 |
| Top Pattern | #17 Mint/Burn Asymmetry |

## Pattern Distribution

| Pattern | Hits | Description |
|------|--:|------|
| #17 Mint/Burn | 500+ | Different accounting for mint vs burn |
| #3 Flash+Reentrancy | 400+ | Flash loan callback reentry path |
| #15 Permit Front-run | 300+ | No deadline on permit |
| #1 Flash Oracle | 200+ | Instant AMM price in valuation |
| #26 Fee Transfer | 200+ | Not verifying received amount |
| #49 Batch DoS | 200+ | One fail → all revert |

## Year Coverage

| Year | Files |
|------|--:|
| 2026 | 55 |
| 2025 | 16 |
| 2024 | 50+ |
| 2023 | 40+ |
| 2022 | 60+ |
| 2021 | 25+ |
| 2020 | 8 |
| 2018 | 3 |
| 2017 | 2 |

---

**58 detection rules × 200+ files × 10 years**
