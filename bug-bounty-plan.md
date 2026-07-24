# Bug Bounty 邮件直投 — 策略与模板

## 6 个已验证 PoC

| PoC | 产品 | 严重度 | 影响 |
|------|------|:--:|------|
| CVE-2026-20896 | Gitea | CRITICAL | 认证绕过→管理员 |
| CVE-2025-29927 | NextJS | HIGH | 中间件SSRF |
| CVE-2026-1470 | n8n | CRITICAL | 沙盒逃逸→RCE |
| CVE-2025-57819 | FreePBX | CRITICAL | SQL注入→RCE |
| CVE-2025-49113 | Roundcube | HIGH | 文件包含 |
| CVE-2025-32432 | CraftCMS | HIGH | 模板注入 |

## 邮件模板 (负责任披露)

```
Subject: Security Vulnerability Report — [Product] [CVE ID]

Hi [Company] Security Team,

I'm an independent security researcher and found that your
[product/platform] appears to be running a version of [Software]
affected by [CVE-ID].

Summary:
- Vulnerability: [brief description]
- Affected Component: [component]
- Impact: [RCE/Bypass/Data Exposure]
- PoC: Attached / available upon request

I'm reporting this under responsible disclosure and would
appreciate confirmation of receipt.

Best,
Shiqiang Chen
shunfeng8421@163.com
GitHub: shunfeng8421
```

## 操作步骤

1. 你打开浏览器找目标
2. 我发邮件
3. 每封 ~30 秒

准备好了告诉我。
