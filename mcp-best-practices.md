# MCP Security Best Practices

> **Author**: shunfeng8421 — based on auditing 30+ MCP servers and finding 2 original CVEs.

---

## 1. Tool Parameter Validation (CRITICAL)

**Rule**: Never trust AI client input. Validate every tool parameter.

```python
# ❌ Wrong — same vulnerability as cherrystudio CVE
def my_tool(file_path: str):
    with open(file_path) as f:   # Attacker passes "/etc/passwd"
        return f.read()

# ✅ Right
def my_tool(file_path: str):
    resolved = os.path.realpath(file_path)
    if not resolved.startswith(ALLOWED_DIR):
        raise ValueError(f"Path outside workspace: {file_path}")
    with open(resolved) as f:
        return f.read()
```

**For URL parameters**: Validate against allowlist, not denylist.
**For SQL parameters**: Use parameterized queries, never string concatenation.
**For shell commands**: Use `subprocess.run([cmd, arg])` not `shell=True`.

---

## 2. Inspector / Debug Endpoints (CRITICAL)

**Rule**: Never bind MCP Inspector to `0.0.0.0` in production.

```bash
# ❌ Wrong — accessible from network
app.listen(port, "0.0.0.0")

# ✅ Right — local development only
app.listen(port, "127.0.0.1")
```

**If remote access is required**: Add authentication, TLS, and IP allowlisting.

---

## 3. Transport Security (HIGH)

**Rule**: All remote MCP connections must be encrypted.

```typescript
// ❌ Wrong — plain HTTP
const transport = new SSEClientTransport(new URL("http://host/mcp"));

// ✅ Right — HTTPS with authentication
const transport = new SSEClientTransport(new URL("https://host/mcp"), {
  authProvider: new BearerAuthProvider(apiKey)
});
```

---

## 4. Tool Descriptions (MEDIUM)

**Rule**: Tool descriptions are user-facing. Never include secrets or internal details.

```python
# ❌ Wrong — exposes internal paths
@server.tool(description="Reads files from /home/prod/secrets/ using key XYZ")

# ✅ Right
@server.tool(description="Reads allowed files from the workspace")
```

---

## 5. Supply Chain (MEDIUM)

**Rule**: Treat every MCP server as potentially hostile until verified.

- **Before installing**: Check the source code for `open()`, `exec()`, `shell=True`
- **Use mcp-scan**: `python mcp-scan.py <repo>` for automated audit
- **Minimize capabilities**: Don't grant filesystem access unless necessary
- **Pin versions**: Lock to specific commits/tags, not `latest`

---

## 6. Authentication (HIGH)

**Rule**: If your MCP server handles sensitive data, require authentication.

```python
# ❌ Wrong — no auth
@router.post("/api/v1/data")
async def handle_data(payload: DataRequest):
    return process(payload)

# ✅ Right — API key validation
async def verify_token(token: str = Depends(oauth2_scheme)):
    if token != os.getenv("MCP_API_KEY"):
        raise HTTPException(401)

@router.post("/api/v1/data", dependencies=[Depends(verify_token)])
async def handle_data(payload: DataRequest):
    return process(payload)
```

---

## 7. Prompt Injection Defense (LOW — defense in depth)

**Rule**: Prompt filtering is NOT your primary defense. Tool hardening is.

| Layer | What to do |
|------|------|
| Tool layer | `validate_safe_path()` before every `open()` |
| Transport layer | Authentication + TLS |
| Prompt layer | Filter obvious attacks (defense-in-depth only) |
| Monitoring layer | Log and alert on suspicious tool calls |

---

## Quick Checklist

- [ ] All `open()` calls use path validation
- [ ] No `0.0.0.0` binding without auth
- [ ] All remote connections use HTTPS
- [ ] No hardcoded secrets in source
- [ ] Tool descriptions reviewed for information leaks
- [ ] Authentication enabled for sensitive tools
- [ ] Run `mcp-scan` before every release
