# CVE 发现方法论 v1.0

## 你的猎场：MCP 服务器路径验证缺陷

### 为什么这个猎场最好
- MCP 协议是2024-2026最热技术，但极少人做安全审计
- 每个MCP服务器都是独立实现，标准化程度低
- 所有MCP服务器都处理文件路径——这是必然的攻击面
- 竞争极低：截至2026-07-13，只有mcp-atlassian和cherrystudio被报告

### 发现步骤（可复制）

```
第1步：搜索
  gh search code "file_path OR filepath mcp language:python stars:>3"
  gh search repos "topic:mcp-server created:>2026-06-01"

第2步：快速判断（30秒/project）
  grep -rn "file_path\|filepath" . --include="*.py" | wc -l     # 有file_path参数?
  grep -rn "validate.*path\|safe_path\|realpath" . --include="*.py" | wc -l  # 有验证?

第3步：如果有file_path但无validate → 90%有漏洞
  grep -B5 "open.*file_path\|open.*path" . -rn | head -5       # 确认直接open()
  grep -rn "@.tool\|register.*tool\|def.*_tool" . -l | head -3  # 确认是MCP工具

第4步：确认无认证
  grep -rn "auth\|api_key\|token\|login" server.py | wc -l      # 0 = 无认证!

第5步：写报告
  - 对照CWE-22
  - 引用已知漏洞（mcp-atlassian）证明模式普遍性
  - 用/etc/passwd做PoC
  - 一行修复方案：validate_safe_path(file_path) before open()
```

### 预期成果
- 扫描10个MCP服务器 → 1-3个漏洞
- 每个CVE用同样的模板报告
- 2周内可提交3-5个CVE

### 扩展方向
- 同模式扩展到: Go/TS MCP服务器（用同等逻辑）
- 同攻击面: 不只是file_path，任何MCP工具参数如果直接传给os函数都是漏洞
