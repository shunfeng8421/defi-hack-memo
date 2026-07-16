# HackerOne Submission Template

## Vulnerability Report Template

```
## Summary
[2-3 sentences describing the vulnerability and impact]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## PoC
```bash
curl -X POST https://target.com/endpoint \
  -d '{"param":"malicious_value"}'
```

## Impact
[What an attacker can do with this vulnerability]

## Suggested Fix
[1-2 sentences on how to fix]
```

## Vulnerable URL Patterns (快速检查清单)
```
/api/v1/users → check for IDOR
/api/v1/files → check for path traversal
/api/v1/search → check for SQL injection
/api/v1/admin → check for missing auth
/api/v1/export → check for SSRF
/api/v1/upload → check for arbitrary upload
/api/v1/settings → check for config injection
/graphql → check for introspection + injection
```

## 快速测试命令
```bash
# Path traversal
curl "https://target.com/download?file=../../../etc/passwd"

# SQL injection
curl "https://target.com/search?q=admin' OR '1'='1"

# SSRF
curl "https://target.com/fetch?url=http://127.0.0.1:6379"

# Missing auth
curl "https://target.com/api/admin/users"

# CORS test
curl -H "Origin: https://evil.com" "https://target.com/api/data"

# IDOR test
curl "https://target.com/api/user/1"
curl "https://target.com/api/user/2"  # Different user, same auth?
```

## Do's and Don'ts
| DO | DON'T |
|------|------|
| Test only in-scope domains | Test out-of-scope systems |
| Stop after confirming the bug | Exfiltrate real user data |
| Use `sleep(3)` for blind SQLi | Run `DROP TABLE` |
| Submit one issue per report | Combine multiple bugs in one report |
| Be professional and helpful | Demand payment or threat | 
