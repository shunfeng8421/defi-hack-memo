# Vulnerability Report: Path Traversal in tai1mo/blogger-cli-mcp MCP Server

**Date**: 2026-07-27
**Audit ID**: AUDIT-2026-07-27-001
**Repository**: https://github.com/tai1mo/blogger-cli-mcp
**Language**: Python
**Severity**: HIGH (CVSS 7.5 - AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)

---

## Summary

The Blogger CLI MCP server exposes two MCP tools that accept arbitrary file paths from the MCP client (LLM agent) and use them to read local files, then upload content to Google Cloud Storage. No path validation or sanitization is performed, allowing an attacker to exfiltrate arbitrary readable files from the server.

## Vulnerability 1: `upload_image_to_gcs` - Arbitrary File Read + Exfiltration

### Affected Tool
`upload_image_to_gcs(file_path: str, content_type: str = None) -> str`

### Data Flow
1. MCP tool definition: `Blogger_mcp_server.py:25` — accepts `file_path: str`
2. Calls `upload_to_gcs(file_path)` at line 38
3. `image_post.py:41` — `Image.open(file_path)` opens the user-controlled path directly
4. Image data is uploaded to GCS at line 77 (`blob.upload_from_string(...)`)
5. Public URL is returned to the caller

### Impact
An attacker can pass any readable file path (e.g., `/etc/passwd`, `~/.ssh/id_rsa`, `.env`, `token.json`) and have its contents uploaded to GCS with a publicly accessible URL. While PIL will fail on non-image files (limiting to image-parseable files), many sensitive files can still be exfiltrated.

### Root Cause
No path validation. The `file_path` parameter from MCP is used directly in `Image.open()`.

### Fix
Add path validation:
```python
import os

ALLOWED_DIRS = [os.path.expanduser("~/blog-images")]

def validate_path(file_path: str) -> str:
    real_path = os.path.realpath(file_path)
    for allowed in ALLOWED_DIRS:
        if real_path.startswith(os.path.realpath(allowed) + os.sep):
            return real_path
    raise ValueError(f"Path {file_path} is outside allowed directories")
```

---

## Vulnerability 2: `replace_html_images_with_gcs` - Directory Traversal + Exfiltration

### Affected Tool
`replace_html_images_with_gcs(html_content: str, base_dir: str) -> str`

### Data Flow
1. MCP tool definition: `Blogger_mcp_server.py:44` — accepts `base_dir: str`
2. Calls `replace_html_images(html_content, base_dir)` at line 57
3. `image_post.py:119` — `os.path.join(base_dir, decoded_src)` joins user-controlled base with image src from HTML
4. `image_post.py:127` — `upload_to_gcs(local_path)` uploads found files

### Impact
An attacker can set `base_dir` to any path (e.g., `/etc`, `~/.ssh`) and via crafted HTML img tags, cause arbitrary image files from that directory tree to be uploaded to GCS. Combined with `..` traversal in img src attributes, even wider access is possible.

### Root Cause
User-controlled `base_dir` with no path restriction.

### Fix
Restrict `base_dir` to a known sandbox directory:
```python
SANDBOX_DIR = os.path.expanduser("~/blog-content")

def validate_base_dir(base_dir: str) -> str:
    real = os.path.realpath(base_dir)
    allowed = os.path.realpath(SANDBOX_DIR)
    if not real.startswith(allowed + os.sep) and real != allowed:
        raise ValueError("base_dir outside allowed directory")
    return real
```

---

## CWE References
- **CWE-22**: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')
- **CWE-73**: External Control of File Name or Path

## CVSS 3.1 Vector
`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N` (7.5 - HIGH)

## Recommendation
Apply path allowlisting to both `upload_image_to_gcs` and `replace_html_images_with_gcs`. Validate that all user-supplied paths resolve within a designated safe directory before any file operations.
