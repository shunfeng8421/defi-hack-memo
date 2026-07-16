# MCP Server Security Audit Checklist

## Pre-Audit (5 min)
- [ ] Clone repo: `git clone <url> /tmp/audit-<name>`
- [ ] Count files: `find . -name "*.py" -o -name "*.ts" -o -name "*.go" | wc -l`
- [ ] Check dependencies: `requirements.txt` / `package.json` / `go.mod`
- [ ] Run strings: `strings * | grep -E "key|secret|password|token|http://"`

## AS1: Tool Parameter Injection (10 min)
- [ ] Search for `open(` / `open(` without `validate_safe_path()`
  - `grep -rn "open(" --include="*.py" --include="*.ts" --include="*.go" | grep -v "test"`
- [ ] Check if file_path comes from MCP tool parameter (not from config)
- [ ] Test: `file_path="../../../etc/passwd"` → should be blocked
- [ ] Test: `file_path="/etc/passwd\x00.jpg"` → null byte bypass
- [ ] Test: `file_path="/proc/self/root/etc/passwd"` → symlink bypass
- [ ] Result: ___

## AS2: Inspector Exposure (5 min)
- [ ] Search for `0.0.0.0` in server startup code
- [ ] Check if authentication is required
- [ ] Check if TLS is enforced
- [ ] Result: ___

## AS3: Client Trust (5 min)
- [ ] Read all tool descriptions — any internal paths revealed?
- [ ] Check for ANSI escape codes in output formatting
- [ ] Check if tool names imply sensitive operations ("admin_delete", etc.)
- [ ] Result: ___

## AS4: Transport Security (5 min)
- [ ] Search for `http://` URLs (should be `https://`)
- [ ] Check for JWT/session management
- [ ] Check for CORS configuration
- [ ] Result: ___

## AS5: Implementation Flaws (15 min)
- [ ] Run Semgrep: `semgrep --config rules/ --no-git-ignore .`
- [ ] Check for `exec(` / `eval(` with user input
- [ ] Check for `shell=True` / `Command::new("sh")`
- [ ] Check for SQL f-string / string concatenation
- [ ] Check for hardcoded secrets: `SECRET = "..."` / `password = "..."`
- [ ] Check for weak random: `math/rand` instead of `crypto/rand`
- [ ] Result: ___

## AS6: Supply Chain (5 min)
- [ ] Check npm/pip maintainer history (recent changes?)
- [ ] Check for suspicious post-install scripts
- [ ] Check if package is pinned to specific version
- [ ] Run `npm audit` / `pip audit`
- [ ] Result: ___

## Report Template
```
Project: 
Date: 
Auditor: shunfeng8421

Issues:
- [HIGH] AS1: file_path injection in <tool_name>
- [MEDIUM] AS4: HTTP transport in <file>
- [LOW] AS3: internal paths in tool description

Recommendations:
1. Add validate_safe_path() to all file operations
2. Enforce HTTPS for all remote transports
3. Remove internal path references from tool descriptions
```

## Time Budget
| Phase | Time |
|------|------|
| Pre-Audit | 5 min |
| AS1-AS6 Scan | 30 min |
| Report Writing | 10 min |
| **Total per project** | **45 min** |
