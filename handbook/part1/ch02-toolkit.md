# Chapter 2: The Security Researcher's Toolkit

## The Minimal Stack

You don't need expensive tools. Everything in this book was built with:

| Tool | Purpose | Cost |
|------|------|:--:|
| Foundry | Solidity testing + deployment | Free |
| Slither | Static analysis | Free |
| VS Code | Code editor | Free |
| Python 3.12 | Scanner scripting | Free |
| Git + GitHub | Version control | Free |

### Why Foundry Over Hardhat

Foundry tests run in Solidity, not JavaScript. This matters because your attack simulations use the exact same execution environment as the real protocol. No translation layer, no JS VM quirks.

```bash
# Install
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Test
forge test -vvv
```

### The 58-Pattern Scanner

The scanner that found 58 distinct vulnerability types across 824 protocols. It's not AI. It's pattern matching with context-aware keyword filtering.

```bash
python defi-scanner.py /path/to/contracts
# Output: JSON report with severity, pattern ID, and fix recommendations
```

### The Exploitarium

A collection of 20+ verified PoC scripts for Web2 vulnerabilities (Gitea, NextJS, n8n, FreePBX, Splunk, etc.). These are your "known-working" templates. When you find a similar attack surface, adapt the PoC.

## The Research Workflow

1. **Acquire**: Clone target repository or access contract source
2. **Scan**: Run the 58-pattern scanner for broad coverage
3. **Deep-dive**: Manually audit scanner hits for false positives
4. **Test**: Write Foundry test to confirm exploit works
5. **Report**: Document finding with description, PoC, and fix
6. **Disclose**: Submit to protocol via responsible disclosure

## The Learning Path

If you're new to DeFi security:
1. Read this handbook (you're doing it now)
2. Run `forge test` on the test suite (105 patterns)
3. Fork the repo and add your own test
4. Pick a real protocol and run the scanner on it
5. Find your first bug

---

*Next: Chapter 3 — How to Read an Exploit Report*
