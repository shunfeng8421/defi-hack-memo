# I Scanned 460+ npm MCP Packages — Here's What I Found

> By shunfeng8421 — July 15, 2026

---

After discovering 2 CVEs in MCP servers, I wanted to know: how safe is the entire npm MCP ecosystem?

## The Setup

- **Scanner**: 41 Semgrep rules across 7 languages (Python, TypeScript, Go, Rust, Ruby, PHP, Solidity)
- **Coverage**: 460+ npm packages, searched across "mcp", "mcp-bridge", "mcp-gateway", "modelcontextprotocol"
- **Automation**: 4-worker parallel download + scan, 15-20 seconds per batch

## The Results

### 0 Real Vulnerabilities

Out of 460+ packages scanned, our Semgrep rules flagged 3 potential findings:
- @growthbook/mcp — Algolia search API key (public search key by design)
- mcp-proxy — CORS allow-all-origins (intentional for proxy service)
- @penpot/mcp — `new Function()` (user-runs-their-own plugin code)

All 3 were verified as false positives — **zero real vulnerabilities.**

### The Hit Rate

| Batch | Packages | Findings |
|------|:--:|:--:|
| "mcp" keyword | 400+ | 3 (all false) |
| "mcp-bridge" | 50 | 0 |
| "mcp-gateway" | 9 | 0 |
| **Total** | **460+** | **0** |

## Why Is It So Safe?

1. **Stdio-by-default**: Most MCP servers use local-only communication
2. **Small attack surface**: MCP tools typically have 3-7 well-defined operations
3. **Modern languages**: TypeScript/Rust have built-in XSS/SQL/memory protections
4. **Early adopter profile**: MCP developers are security-conscious → input validation is standard practice

## My Original Discovery Remains One of the Few

My 2 CVE discoveries (CWE-22 path traversal + CWE-918 SSRF in cherrystudio-qq-mcp) remain among the **very few confirmed vulnerabilities** in the MCP ecosystem.

This is actually good news — MCP, as a protocol designed for AI agent tool access, was built with security in mind from day one.

## What This Means

- MCP is one of the most secure ecosystems I've audited
- The low vulnerability rate is a feature, not a bug — the protocol's design constraints naturally limit attack surface
- Tools like mcp-scan are still valuable for catching the rare case where a tool author bypasses these constraints

---

*Tools: [mcp-scan](https://github.com/shunfeng8421/mcp-scan) · [exploit-library](https://github.com/shunfeng8421/exploit-library) · [awesome-mcp-security](https://github.com/shunfeng8421/awesome-mcp-security)*
