# Appendix D: Scanner Configuration Guide

```bash
# Run scanner on a directory
python defi-scanner.py /path/to/contracts/

# Output: JSON report with severity, pattern ID, and fix recommendations
# JSON saved to: /path/to/contracts/scan-results.json
```

## Adding a New Pattern

Edit `defi-scanner.py`, add to the PATTERNS dict:

```python
NEW_ID: {
    "name": "Pattern Name",
    "severity": "CRITICAL",  # CRITICAL | HIGH | MEDIUM | LOW
    "regex": [r'vulnerable\(\)', r'\.badPattern'],
    "keyword": ["match", "these", "!not", "!these"],
    "description": "What this pattern detects",
    "fix": "How to fix it"
}
```

## Severity Levels

| Level | Meaning |
|:--:|------|
| CRITICAL | Direct fund loss, no preconditions |
| HIGH | Fund loss with specific preconditions |
| MEDIUM | Protocol disruption or limited fund risk |
| LOW | Gas inefficiency or UX degradation |

Scanner: `defi-scanner.py` (2,847 lines, 66 patterns)
