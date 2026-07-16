### 16. Auth URL解析不一致 → 认证绕过
```
URL: /api/v1/raw/{real_id}/...
路由层: id = real_id
认证层: id = raw (静态路径段被误认为ID)
→ 查不到 raw 的密钥 → 跳过认证 → 绕过！
```
- 搜法: 认证中间件 + URL解析 + `req.path.split("/")[N]` 模式
- 来源: Apollo ConfigService (Day 4, 2026-07-13)
- 变种: 任何 URL 包含静态段(如 /download/、/raw/、/public/)时，
  认证中间件可能把静态段当ID解析
- Semgrep: 搜认证逻辑中的 `split("/")` 调用，检查索引是否正确
