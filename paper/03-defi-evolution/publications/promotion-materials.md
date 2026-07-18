# Citation & Promotion Materials

## BibTeX Citations

### Paper 1: MCP Server Security Taxonomy

```bibtex
@misc{chen2026mcpsecurity,
  author       = {Shiqiang Chen},
  title        = {An Empirical Study of MCP Server Security: 6 Attack Surfaces from 30+ Audits},
  year         = {2026},
  month        = jul,
  doi          = {10.5281/zenodo.21370417},
  url          = {https://doi.org/10.5281/zenodo.21370417},
  publisher    = {Zenodo},
  note         = {Preprint}
}
```

### Paper 2: Prompt Injection Re-framing

```bibtex
@misc{chen2026promptinjection,
  author       = {Shiqiang Chen},
  title        = {Prompt Injection is Not an AI Problem: Why MCP Tool Hardening Matters},
  year         = {2026},
  month        = jul,
  doi          = {10.5281/zenodo.21370438},
  url          = {https://doi.org/10.5281/zenodo.21370438},
  publisher    = {Zenodo},
  note         = {Preprint}
}
```

---

## X/Twitter Promotion

### Version A — Thread (推荐)

**Tweet 1/4:**
> After auditing 30+ MCP servers, we found 6 distinct attack surfaces that most implementations miss — and 2 new CVEs.
> 
> MCP is the backbone of AI agent interoperability. But its security model? Almost non-existent.
> 
> Here's what we discovered: 🧵

**Tweet 2/4:**
> The 6 MCP attack surfaces:
> 1. Tool Parameter Injection — the most dangerous
> 2. Inspector Exposure — internal state leaks
> 3. Client Trust Exploitation — impersonation
> 4. Transport Security — MITM on stdio/SSE
> 5. Implementation Flaws — code-level bugs
> 6. Supply Chain — poisoned MCP packages

**Tweet 3/4:**
> But here's the real insight:
> 
> Prompt injection isn't an AI alignment problem. It's a tool security problem.
> 
> If your MCP tools validate inputs at the boundary (not the LLM), 90% of injection attacks disappear. "Validate at the boundary, not the model."

**Tweet 4/4:**
> Both papers now on Zenodo with DOIs:
> 
> 📄 MCP Security Taxonomy: https://doi.org/10.5281/zenodo.21370417
> 📄 Prompt Injection Re-framing: https://doi.org/10.5281/zenodo.21370438
> 
> GitHub: https://github.com/shunfeng8421/awesome-mcp-security
> 
> Open access, CC-BY-4.0. Feedback welcome.

### Version B — Single Tweet (简洁版)

> Audited 30+ MCP servers → found 6 attack surfaces, 2 CVEs.
> 
> Key finding: Prompt injection is a tool security problem, not an AI alignment one. "Validate at the boundary, not the model."
> 
> 📄 Papers (Zenodo, open access):
> • DOI: 10.5281/zenodo.21370417
> • DOI: 10.5281/zenodo.21370438

---

## Blog Post Outline

### Title Options
- "The MCP Security Wake-Up Call: What 30+ Audits Revealed"
- "Prompt Injection is Not an AI Problem — And That Changes Everything"
- "6 Ways Your MCP Server Can Be Exploited (And How to Fix Them)"

### Structure
1. **Why MCP security matters now** — MCP is becoming the standard protocol for AI agent tools. Claude, Gemini, Copilot all adopting it. But security is lagging behind adoption.
2. **The 6 attack surfaces** — Brief walk-through of each with concrete examples
3. **The prompt injection insight** — Why model-level defenses are the wrong layer. Tool input validation is the right answer.
4. **What needs to happen** — Protocol-level security specs, implementation hardening guides, community auditing infrastructure.
5. **Links to papers + GitHub**
