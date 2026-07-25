# Chapter 22: Building a Security Scanner

*"A good scanner finds patterns. A great scanner knows when a pattern is a false positive."*

---

## The 58-Pattern Scanner

The scanner that supports this book—`defi-scanner.py`—scanned 824 DeFi protocol repositories and identified 58 distinct vulnerability patterns across 17 attack domains. It is 2,847 lines of Python. It uses zero machine learning. It runs on any machine with Python 3.12+.

This chapter explains how to build your own scanner and how the design decisions in our scanner reflect the lessons of every previous chapter.

---

## Architecture

The scanner has three components:

### 1. Pattern Definitions

Each pattern is a Python dictionary with five fields:

```python
PATTERNS = {
    1: {
        "name": "Flash Loan + Spot Price Oracle",
        "severity": "CRITICAL",
        "regex": [r'getReserves\(\)', r'\.balance\b'],
        "keyword": ["price", "oracle", "!TWAP", "!cumulative", "!Chainlink"],
        "description": "Instant spot price used as oracle input",
        "fix": "Use TWAP oracle or Chainlink with staleness check"
    },
    # ... 57 more patterns
}
```

The `regex` field matches vulnerable code patterns. The `keyword` field provides context: positive keywords that should be present and negated keywords (prefixed with `!`) that should be absent. A file that uses `getReserves()` AND contains `TWAP` in its imports is likely using the oracle correctly. A file that uses `getReserves()` WITHOUT any of the negated keywords is suspicious.

### 2. File Processing

The scanner walks a directory tree, reads every `.sol` and `.rs` file, and applies every pattern. Solana patterns (51-58) are only applied to `.rs` files. DeFi patterns (1-50) are only applied to `.sol` files. This file-type filtering eliminates the most common class of false positives: Solana patterns matching Solidity keywords.

### 3. Report Generation

The scanner outputs JSON with structured findings including file paths, line numbers, pattern IDs, severity levels, and fix recommendations. The JSON format enables integration with CI pipelines and the AI Auditor.

---

## False Positive Control

The most important feature of any scanner is not how many patterns it has. It is how many false positives it generates. A scanner that flags 1,000 findings, 980 of which are false positives, wastes the auditor's time. A scanner that flags 20 findings, 15 of which are real, makes the auditor more effective.

Our scanner achieves an estimated 70% true positive rate through three mechanisms:

1. **File-type filtering**: Solana patterns never fire on Solidity code. This alone eliminated 15% of false positives in testing.

2. **Negated keywords**: The `!chainId` keyword means "this pattern only applies if `chainId` is NOT present." A bridge that correctly includes chainId in its signatures will never trigger the cross-chain replay pattern.

3. **Severity weighting**: CRITICAL and HIGH findings are prioritized in the report. LOW severity findings are included in the JSON for completeness but not surfaced in the summary, reducing noise.

---

## Extending the Scanner

To add a new pattern, define it in the PATTERNS dictionary and test it against known-positive and known-negative examples. A good pattern:

- Has a clear description that anyone can understand
- Has regex that matches the vulnerable code precisely
- Has negated keywords that prevent false positives
- Has a fix recommendation that is specific and actionable

A bad pattern:
- Matches too broadly (every `transfer()` function)
- Has no negated keywords (no false positive protection)
- Has a vague fix ("be more careful")

---

*Next: Chapter 23 — Writing Effective Tests*
