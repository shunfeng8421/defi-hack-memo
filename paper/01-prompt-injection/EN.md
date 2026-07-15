# Prompt Injection is Not an AI Problem: Why MCP Tool Hardening Matters

**Authors**: Shiqiang Chen (Independent Researcher)

**Date**: July 14, 2026 | **DOI**: 10.5281/zenodo.21370438

---

## Abstract

We demonstrate that prompt-level filtering provides only 50% protection against injection attacks, while simple input validation at the MCP tool layer provides 100% protection. The fix is `validate_safe_path()`.

![Attack Success Rate](figures/01-prompt-injection/fig1-attack-success.pdf)

*Figure 1: Prompt Filter vs Tool-Layer Filter across 6 attack techniques*

## Key Findings

| Defense | Success Rate |
|------|:--:|
| No defense | 83% |
| Prompt filter | 50% |
| Tool-layer filter | **0%** ✅ |

## Why Prompt Filtering Fails

- JSON-nested tool calls bypass structure filters
- Multilingual injection bypasses keyword filters
- Benign-looking paths are indistinguishable from malicious ones

## Why Tool Hardening Works

One line of code eliminates the entire class of prompt-injection-to-path-traversal attacks:

```python
def validate_safe_path(path, base_dir):
    full = os.path.realpath(os.path.join(base_dir, path))
    if not full.startswith(os.path.realpath(base_dir)):
        raise SecurityError("Path traversal detected")
    return full
```

## Real-World Case: cherrystudio-qq-mcp

Two independently discovered CVEs:
- **CWE-22**: `qq_upload_file(file_path)` → `open(file_path)` without validation
- **CWE-918**: `recognize_image(url)` → `requests.get(url)` without URL validation

---

Tools: [mcp-scan](https://github.com/shunfeng8421/mcp-scan), [awesome-mcp-security](https://github.com/shunfeng8421/awesome-mcp-security)
