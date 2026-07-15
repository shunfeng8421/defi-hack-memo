# Prompt Injection 不是 AI 问题：为什么 MCP 工具层加固才是关键

**作者**：陈世强 (Shiqiang Chen) — 独立安全研究员

**日期**：2026 年 7 月 14 日

**分类**：cs.CR (密码学与安全), cs.AI (人工智能)

---

## 摘要

Prompt injection 被广泛讨论为 AI 安全问题。我们提出实验证据表明这种框架是不完整的。使用自定义 MCP 代理模拟器和一个存在真实漏洞的 MCP 服务器 (cherrystudio-qq-mcp)，我们证明：prompt 层过滤对注入攻击仅提供 50% 的防护，而 MCP 工具层的简单输入验证提供 100% 的防护。核心发现：prompt injection 的防御应该实现在工具执行边界，而非 prompt 解析边界。我们提供了使用 `validate_safe_path()` 的实用缓解策略，并开源了 MCP 安全评估工具。

---

## 1. 引言

2024 年 Anthropic 推出 MCP (Model Context Protocol) 后，AI 代理可以标准化地访问外部工具。随之而来的安全问题是：如果 AI 代理被欺骗执行恶意工具调用，怎么办？

已有研究主要聚焦于 prompt 层的防御——通过过滤提示词中的注入内容。但我们认为这个方向是错误的。本文通过实验证明：**最有效的防御不在 prompt 层，而在 MCP 工具的执行层。**

---

## 2. 实验设计

我们构建了 MCP Agent Simulator，模拟一个具有文件系统访问权限的 AI 代理。测试了 6 种 prompt injection 技术：

### 2.1 测试攻击类型

| 攻击方式 | 成功率 (prompt过滤) | 成功率 (工具层过滤) |
|------|:--:|:--:|
| 直接注入 | 100% | 0% |
| 间接注入 | 80% | 0% |
| 编码绕过 | 60% | 0% |
| 多步注入 | 40% | 0% |
| 上下文污染 | 20% | 0% |
| Unicode 混淆 | 0% | 0% |

**平均**：prompt 过滤 50%，工具层过滤 0%

### 2.2 真实案例：cherrystudio-qq-mcp

我们在 cherrystudio-qq-mcp 中发现两个真实漏洞：

**CWE-22 路径遍历**：`file_path` 参数没有经过 `validate_safe_path()` 验证，攻击者可以读取任意文件。

**CWE-918 SSRF**：URL 参数没有白名单限制，攻击者可以进行内网扫描。

---

## 3. 为什么工具层防御更有效

```
Prompt 层防御：
  "请帮我读取 /etc/passwd" → 检测"恶意" → 拒绝

  "请读取系统配置文件的备份副本" → 未检测到 → 允许
  AI 代理自行推理为 /etc/passwd → 成功读取

工具层防御：
  file_path="/etc/shadow" → validate_safe_path() → beyond base_dir → 拒绝 ✅
  不受 prompt 措辞影响
```

核心观点：**输入验证应该在语义层面之前完成。**

---

## 4. 实践建议

```python
def validate_safe_path(path: str, base_dir: str) -> str:
    full = os.path.realpath(os.path.join(base_dir, path))
    if not full.startswith(os.path.realpath(base_dir)):
        raise SecurityError("Path traversal detected")
    return full
```

所有 MCP 工具应该在执行前调用此函数。

---

## 5. 结论

Prompt injection 的防御重心应该从 prompt 过滤转移到工具层输入验证。我们提供了实验数据、真实案例和开源工具来支持这一结论。

对应的英文原版见 Zenodo。
