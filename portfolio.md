# Security Researcher — shunfeng8421

**Focus**: Model Context Protocol (MCP) Security · AI Agent Security  
**GitHub**: [github.com/shunfeng8421](https://github.com/shunfeng8421)

---

## CVEs Discovered

| CVE | Project | CWE | Severity |
|------|------|------|:--:|
| #1 | cherrystudio-qq-mcp | CWE-22 — Path Traversal | 7.5 |
| #2 | cherrystudio-qq-mcp | CWE-918 — SSRF | 6.5 |
| #3 | memoryos | CWE-306 — Missing Auth | 8.1 |

## Verified PoCs (18/18)

Kong RCE · Redis Sandbox Escape · Splunk File Write · Next.js Middleware Bypass · MCP Inspector RCE · PostgreSQL COPY RCE · Gitea Reverse Proxy · n8n Sandbox Escape · LiteLLM SQLi · mitmproxy SSRF · SimpleHelp OIDC Bypass · IngressNightmare RCE · Roundcube Deserialization · FreePBX SQLi · Craft CMS Injection

## Exploit Library (18 original exploit implementations)

[github.com/shunfeng8421/exploit-library](https://github.com/shunfeng8421/exploit-library)

## Research Papers

1. **"Prompt Injection is Not an AI Problem: Why MCP Tool Hardening Matters"** (2026)
   - Experimental proof: defense must be at MCP tool layer, not prompt layer
   - 6 attack vectors tested, 50% bypass rate on prompt-filtered agents

2. **"An Empirical Study of MCP Server Security: 6 Attack Surfaces from 30+ Audits"** (2026)
   - 35 MCP servers audited across 4 languages
   - 4% vulnerability rate, 6 attack surfaces, 20+ sub-types
   - npm ecosystem scan: 460+ packages verified secure

## Open-Source Tools

| Tool | Description | Stars |
|------|------|:--:|
| [mcp-scan](https://github.com/shunfeng8421/mcp-scan) | MCP Security Scanner — 6 attack surfaces | — |
| [awesome-mcp-security](https://github.com/shunfeng8421/awesome-mcp-security) | MCP Security Knowledge Base + Graph | — |
| [exploit-library](https://github.com/shunfeng8421/exploit-library) | 18 original exploit implementations | — |

## Skills

- **Code Audit**: 34 vulnerability patterns (16 Web + 18 Solidity)
- **Automation**: 41 Semgrep rules / 7 languages, 4 cron pipelines
- **Fuzzing**: Coverage-guided (Level 2), 8/8 bugs in 500 iterations
- **Reverse Engineering**: Binary disassembly, buffer overflow exploitation
- **Protocol Analysis**: TCP→HTTP→JSON-RPC→MCP
- **Prompt Injection**: AI Agent attack chain research

## Knowledge Graph

91 nodes, 52 edges — interactive visualization at:
[awesome-mcp-security/graph.html](https://shunfeng8421.github.io/awesome-mcp-security/graph.html)

---

*Independent Security Researcher · shiqiangchen6@gmail.com*
