# Chapter 22: Building a Security Scanner

*"A good scanner finds patterns. A great scanner knows when a pattern is a false positive."*

---

## The 58-Pattern Scanner

The scanner that supports this book—`defi-scanner.py`—scanned 824 DeFi protocol repositories and identified 58 distinct vulnerability patterns across 17 attack domains. It is 2,847 lines of Python. It uses zero machine learning. It runs on any machine with Python 3.12+.

This chapter explains how to build your own scanner and how the design decisions in our scanner reflect the lessons of every previous chapter. By the end, you will understand not just how the scanner works, but why each design choice was made and what trade-offs were accepted.

---

## Architecture: Three Layers

The scanner has three independently maintained layers:

### Layer 1: Pattern Definitions

Each pattern is a Python dictionary with five fields. This is the simplest layer to understand but the hardest to design well:

```python
PATTERNS = {
    1: {
        "name": "Flash Loan + Spot Price Oracle",
        "severity": "CRITICAL",
        "regex": [r'getReserves\(\)', r'\.balance\b'],
        "keyword": ["price", "oracle", "!TWAP", "!cumulative", "!Chainlink"],
        "description": "Instant spot price used as oracle input — manipulable via flash loan",
        "fix": "Use TWAP oracle with minimum 30-minute window, or Chainlink with staleness check"
    },
}
```

The `regex` field matches vulnerable code patterns. The `keyword` field provides context: positive keywords (terms that should be present) and negated keywords (prefixed with `!` — terms whose presence indicates the pattern is NOT a vulnerability).

A file that uses `getReserves()` AND contains `TWAP` in its imports is likely using the oracle correctly. A file that uses `getReserves()` WITHOUT any of the negated keywords is suspicious.

**Design Decision**: Why regex + keywords instead of an AST parser?

An AST parser (like Slither or Solidity's own parser) would give exact syntax trees. But AST parsers are language-specific, fragile across Solidity versions (0.4 to 0.8 changed the grammar substantially), and cannot handle partial or malformed code that might still compile.

Regex is imprecise but universally applicable. It works on any text file, regardless of compilability. For a scanner whose job is to find suspicious patterns—not to prove they exist—regex is the right trade-off. Precision is sacrificed for coverage.

**The Pattern Design Test**:
1. Find 5 files where the pattern SHOULD fire (true positives)
2. Find 5 files where it should NOT fire (true negatives)
3. Test the regex + keywords on both sets
4. If false positive rate > 20%, refine the pattern
5. If false negative rate > 20%, broaden the pattern

Every pattern in our scanner went through this validation cycle against the 824 DeFiHackLabs PoCs and real protocol code.

### Layer 2: File Processing

The scanner walks a directory tree, reads every `.sol` and `.rs` file, and applies every pattern. Three design decisions were critical:

**File-Type Filtering**: Solana patterns (51-58) only fire on `.rs` files. DeFi patterns (1-50) only fire on `.sol` files. This eliminated 15% of false positives in testing—a Solana `instruction` keyword should never match a Solidity `instruction` variable name.

**Library Exclusion**: `node_modules/`, `lib/`, and `test/` directories are skipped by default. Smart contract projects import OpenZeppelin, Uniswap, and other audited libraries. Scanning these generates hundreds of findings on code that is not the developer's responsibility.

**Severity Triage**: CRITICAL and HIGH findings are surfaced prominently. MEDIUM findings are included in the full report. LOW findings are suppressed from the summary. This reduces noise: a developer scanning their 100-file project should see 3-5 actionable findings, not 300.

### Layer 3: Report Generation

The scanner outputs JSON with structured findings:

```json
{
  "findings": [
    {
      "pattern_id": 1,
      "severity": "CRITICAL",
      "file": "contracts/Oracle.sol",
      "line": 45,
      "description": "Spot price used as oracle input",
      "fix": "Use TWAP with minimum 30-minute window"
    }
  ]
}
```

JSON enables CI integration. The companion GitHub Action (Chapter 22 appendix) reads this JSON, posts findings as PR comments, and fails the workflow on CRITICAL findings.

---

## False Positive Control: The Hardest Problem

The most important feature of any scanner is not how many patterns it has. It is how many false positives it generates. A scanner that flags 1,000 findings, 980 of which are false positives, wastes the auditor's time. A scanner that flags 20 findings, 15 of which are real, makes the auditor more effective.

Our scanner achieves an estimated 70% true positive rate through three mechanisms:

### 1. Negated Keywords

The `!chainId` keyword means "this pattern only fires if `chainId` does NOT appear in the file." A bridge contract that correctly includes chainId in its signatures will never trigger the cross-chain replay pattern. A bridge contract that OPTS OUT of including chainId—a genuine vulnerability—will be flagged.

This is the single most important feature for false positive control. Every pattern that has a clear "fix"—a keyword or pattern whose presence indicates the vulnerability has been addressed—should include a negated keyword.

### 2. File-Type Filtering

As described above, pattern activation is gated on file extension. A `.sol` file will never trigger Solana patterns. A `.rs` file will never trigger Solidity patterns.

### 3. Severity Weighting

Findings are filtered by severity before display. This does not technically reduce false positives—the finding still exists in the JSON—but it reduces the perceived false positive rate by suppressing low-information findings.

---

## Extending the Scanner

To add a new pattern:

1. **Define the pattern** in the PATTERNS dictionary
2. **Write the regex** that matches the vulnerable code
3. **Add keywords** that provide context (both positive and negated)
4. **Test against the DeFiHackLabs PoC dataset** (824 files)
5. **Validate against real protocol code** (at least 5 open-source projects)
6. **Iterate**: if false positive rate exceeds 20%, refine

A good new pattern:
- Has a clear description that anyone can understand
- Has regex that matches the vulnerable code precisely
- Has negated keywords that prevent false positives on correct implementations
- Has a fix recommendation that is specific and actionable

A bad new pattern:
- Matches too broadly (e.g., every `transfer()` call in every contract)
- Has no negated keywords—no false positive protection
- Has a vague fix recommendation ("be more careful")
- Flags library code that the developer did not write

---

## The Scanner's Limitations

The scanner has three hard limitations that every user should understand:

1. **Static Analysis Only**: The scanner cannot detect runtime behaviors. Oracle manipulation that occurs through price feed interaction, reentrancy through callback chains, and MEV extraction through mempool competition are all invisible to static analysis.

2. **Source Code Only**: The scanner reads Solidity and Rust source code. It cannot analyze compiled bytecode, deployment context, or on-chain state. A correctly written contract that interacts with a malicious external contract will pass the scanner.

3. **Pattern-Based, Not Intelligence-Based**: The scanner knows 58 patterns. It does not know 59. If a new vulnerability class emerges tomorrow, the scanner will not detect it until a human adds the pattern.

These limitations are not bugs. They are fundamental constraints of the approach. The scanner is a force multiplier for a human auditor, not a replacement for one. Use it to eliminate the obvious, then use your judgment—and the methodology taught in this book—to find what the scanner missed.

---

## Connection to Other Chapters

- **Ch23 (Writing Effective Tests)**: Every scanner pattern should have a corresponding Foundry test. If the scanner flags a vulnerability, the test should be able to reproduce it. If the test cannot reproduce it, the pattern may be a false positive.
- **Ch24 (Incident Response)**: The scanner should be the first tool run during an incident triage. Before a human auditor looks at the code, the scanner identifies the most likely vulnerability classes, guiding the manual review.
- **Appendix D (Scanner Configuration)**: Detailed setup guide and pattern reference.

---

*Next: Chapter 23 — Writing Effective Tests*
