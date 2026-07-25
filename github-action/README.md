# DeFi Security Scanner — GitHub Action

Free security scan on every PR. 58 automated detection rules for Solidity and Rust.

## Quick Start

Add to `.github/workflows/security-scan.yml`:

```yaml
name: Security Scan
on: [pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: shunfeng8421/defi-hack-memo/github-action@master
```

## Features

- 🔍 Scans all `.sol` and `.rs` files automatically
- 🔴 Fails PR on CRITICAL findings
- 📊 Outputs finding counts for CI integration
- 🆓 Completely free and open-source

## Inputs

| Input | Default | Description |
|------|------|------|
| `path` | `.` | Directory to scan |
| `fail_on` | `CRITICAL` | `CRITICAL` / `HIGH` / `NEVER` |

## Scanner

Powered by the [DeFi Security Handbook](https://github.com/shunfeng8421/defi-hack-memo) — 66 attack patterns, 24 chapters, 105 Foundry tests.

## Author

Shiqiang Chen — Independent Security Researcher
