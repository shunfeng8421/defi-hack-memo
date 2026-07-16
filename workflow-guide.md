# 安全研究员完整工作流

## 日常运转

### 上午 (自动化产出)
```
09:00  daily-scan.py       ← 依赖反查 + Exploit-DB
10:00  NVD 数据库同步       ← 新 CVE 情报
12:00  自动审计流水线        ← 扫描→推理→报告
```

### 下午 (高价值手工)
```
14:00  审计最热 GitHub 项目  ← 用 mcp-scan
16:00  写 exploit            ← 武器库积累
18:00  论文/文档             ← 影响力建设
```

## 工具链

### 扫描层
| 工具 | 命令 | 覆盖 |
|------|------|------|
| mcp-scan | `python mcp-scan.py <repo>` | MCP 6 攻击面 |
| Semgrep | `semgrep --config rules/` | 41 条/7 语言 |
| npm 批量 | `python npm_mcp_scan.py 100 0 mcp` | npm 生态 |

### 推理层
| 工具 | 命令 |
|------|------|
| reasoner.py | `python reasoner.py <path>` |
| audit_pipeline | `python audit_pipeline.py <path>` |

### 知识层
| 工具 | 用途 |
|------|------|
| knowledge-graph.json | 91 节点关系网 |
| knowledge_base_server.py | MCP 服务→AI 可查询 |
| graph.html | 交互式可视化 |

## 技能栈

| 技能 | 用途 |
|------|------|
| Fuzzing L1/L2 | 自动发现输入验证绕过 |
| 逆向工程 | 理解二进制+提取密钥 |
| 协议分析 | TCP→HTTP→MCP 4层审计 |
| 内存利用 | 缓冲区溢出 exploit 编写 |
| Prompt Injection | AI Agent 攻击链研究 |

## 产出渠道

| 产类型 | 平台 | 周期 |
|------|------|------|
| CVE 报告 | GitHub Issue / 邮件 | 每发现即报 |
| 论文 | GitHub Pages / arXiv | 每月 1 篇 |
| 博客 | Dev.to / 知乎 | 每周 1 篇 |
| exploit | exploit-library | 每 CVE 1 个 |

## 快速审计清单 (45分钟)

1. clone → 2. Semgrep 扫 → 3. mcp-scan → 4. 手工查 API 端点
5. 确认认证 → 6. 数据流追踪 → 7. 写报告

## 你现在的数据

- CVE: 2 原创 + 18 验证
- Exploit: 18 自写
- 规则: 41 Semgrep / 7 语言
- 模式: 34
- 论文: 2
- 工具: 7
- 图谱: 91 节点 / 52 边
- 扫描: 530+ npm 包
