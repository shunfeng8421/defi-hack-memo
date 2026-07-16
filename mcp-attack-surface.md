# MCP 协议完整攻击面 v1.0

## 概述
MCP (Model Context Protocol) = AI 客户端 ↔ MCP 服务器的标准化协议。
核心问题：**客户端和服务器对"信任边界"的理解不一致。**

---

## 攻击面 1: 工具参数注入

| 子类型 | 描述 | 实例 |
|------|------|------|
| file_path 服务器解析 | 客户端以为 path 在本地，实际在服务器 | cherrystudio, mcp-atlassian |
| URL SSRF | 工具接受 URL 参数 → 服务器 fetch → SSRF | cherrystudio #2 |
| Shell 注入 | 工具参数拼接到 shell 命令 | Phantom |

**搜法**: MCP 工具定义中的 `file_path`/`url`/`command` 参数 → 服务器端直接使用

---

## 攻击面 2: MCP Inspector 暴露

| 子类型 | 描述 | 实例 |
|------|------|------|
| 绑定 0.0.0.0 | Inspector 默认监听所有网口 | CVE-2025-49596, CVE-2026-23744 |
| 无认证 | Inspector 无需登录即可触发工具 | 两个 CVE 都有 |
| 工具安装触发 RCE | 通过 Inspector 安装任意 MCP 服务器 → RCE | MCPJam Inspector |

---

## 攻击面 3: MCP 客户端信任

| 子类型 | 描述 |
|------|------|
| 工具描述中毒 | MCP 服务器返回恶意工具描述 → 欺骗 AI 代理 |
| 服务器冒充 | 同名 MCP 服务器替换 → 窃取 AI 上下文 |
| 凭证窃取 | MCP 服务器请求 API Key 作为 "必需参数" |

---

## 攻击面 4: 传输层

| 子类型 | 描述 |
|------|------|
| stdio 劫持 | 本地 MCP 进程被替换 |
| SSE 中间人 | HTTP MCP 连接未加密 |
| WebSocket 重放 | MCP 消息无签名 → 可重放 |

---

## 攻击面 5: MCP 服务器实现缺陷

| 子类型 | 描述 |
|------|------|
| 路径遍历 | 文件操作无安全路径验证 |
| SSRF | HTTP 工具无 IP 过滤 |
| 命令注入 | shell=True + 用户输入 |
| SQL 注入 | MCP 工具拼接 SQL |
| 弱默认密钥 | JWT_SECRET = "auth_token" |
| eval() / exec() | 工具内执行未沙箱化的代码 |

---

## 攻击面 6: MCP 供应链

| 子类型 | 描述 |
|------|------|
| npm 包替换 | MCP 服务器作为 npm 包 → 被投毒 |
| 依赖漏洞 | MCP 服务器依赖已知漏洞库 |
| 配置泄露 | MCP 配置文件提交到公开仓库 |
