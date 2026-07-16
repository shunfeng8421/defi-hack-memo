# HERMES Vulnerability Disclosure Policy

## 编号系统

格式: `HERMES-YYYY-NNN`
- YYYY: 发现年份
- NNN: 三位序号（按发现顺序）

| ID | CVE | 项目 | 严重性 |
|------|------|------|:--:|
| HERMES-2026-001 | cherrystudio-qq-mcp CWE-22 | 路径遍历 | 7.5 |
| HERMES-2026-002 | cherrystudio-qq-mcp CWE-918 | SSRF | 6.5 |
| HERMES-2026-003 | memoryos CWE-306 | 无认证 | 8.1 |

## 披露节奏

```
Day 0   发现漏洞 → 分配 HERMES-ID
Day 7   通知维护者 (GitHub Issue / 安全邮箱)
Day 14  无响应 → 第二次通知
Day 30  仍无响应 → 提交 CVE 编号分配
Day 90  公开发布（含 exploit + 论文 + 博客）
```

## 报告模板

参见 `D:/hermes/skills/security-researcher/hackerone-template.md`

## 公开平台

- [GitHub Issues](https://github.com/shunfeng8421/security-audit)
- [awesome-mcp-security](https://shunfeng8421.github.io/awesome-mcp-security/)
- [exploit-library](https://github.com/shunfeng8421/exploit-library)

---

*Policy effective: 2026-07-15*
