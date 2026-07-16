# How I Audited 50 MCP Servers and Found 6 Attack Surfaces

> By [shunfeng8421](https://github.com/shunfeng8421) — July 14, 2026

---

I spent a week auditing MCP (Model Context Protocol) servers. Here's what I learned.

## The Method

1. Search GitHub for `topic:mcp-server` across Python, TypeScript, Go, and Rust
2. Scan each server with [mcp-scan](https://github.com/shunfeng8421/mcp-scan) — an automated security assessment tool I built
3. Manually verify every finding
4. Report verified vulnerabilities to maintainers

## The 6 Attack Surfaces

### 1. Tool Parameter Injection (3% of servers vulnerable)

MCP tools accept parameters from AI clients. When those parameters are treated as trusted input, injection happens.

**Real finding**: `cherrystudio-qq-mcp` accepts `file_path` from MCP clients and calls `open(file_path)` on the server — no path validation. Any MCP client can read `/etc/passwd`.

**Search for**: `file_path` parameters + `open()` without `validate_safe_path()`

### 2. Inspector / Debugger Exposure

MCP inspection tools are designed for local development, but many bind to `0.0.0.0` — exposing them to the network.

**Real finding**: CVE-2025-49596 — MCP Inspector binds `0.0.0.0` with no authentication. CVE-2026-23744 — MCPJam Inspector same pattern.

### 3. Client Trust Exploitation

MCP servers control what tools they expose and what descriptions those tools have. A malicious server can:
- Trick the AI into calling dangerous tools
- Hide malicious actions via ANSI escape codes in output
- Phish for API keys by declaring them as "required parameters"

### 4. Transport Layer

MCP supports stdio (local) and HTTP/SSE (remote). Remote connections often lack:
- Encryption (plain HTTP)
- Message signing (replay attacks possible)
- Session management (no token rotation)

### 5. Implementation Flaws

Same vulnerabilities as any web service, just in MCP context:
- SQL injection in tool handlers
- Command injection via `shell=True`
- Weak default secrets (Flowise's `JWT_SECRET = "auth_token"`)
- eval/exec without sandbox

### 6. Supply Chain

MCP servers are distributed as npm packages, pip packages, or GitHub repos. Supply chain risks include package takeover, dependency vulnerabilities, and config file leaks.

## The Numbers

| Metric | Count |
|------|:--:|
| Servers audited | 50+ |
| Languages covered | Python, TypeScript, Go, Rust |
| Verified vulnerabilities | 20 (18 known + 2 original) |
| Overall vulnerability rate | ~4% |

## Tools

- [mcp-scan](https://github.com/shunfeng8421/mcp-scan) — Automated MCP security scanner
- [awesome-mcp-security](https://github.com/shunfeng8421/awesome-mcp-security) — Curated MCP security resources

## Key Takeaway

MCP servers are generally well-coded. The vulnerability rate (~4%) is much lower than typical web applications. But when vulnerabilities exist, they're usually severe — because MCP tools have direct access to the server's filesystem, network, and processes.

**Always audit an MCP server before connecting it to your AI agent.**
