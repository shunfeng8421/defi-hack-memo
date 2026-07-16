# Bug Bounty 快速启动指南

## 你的武器库
- 34 漏洞模式 (16 Web + 18 Solidity)
- 32 条 Semgrep 规则 (5 语言)
- mcp-scan 自动扫描器
- 18 个自写 exploit
- daily-scan.py 依赖反查脚本

## 第一天: 选目标

**选目标三原则**:
1. 开源优先 (有源码 = 审计优势)
2. 低竞争 (避开 Google/Meta/GitLab 万人坑)
3. 匹配技能 (Python/Go/TS/AI 工具)

**推荐首发目标**:
| 项目 | 类型 | 赏金 | 原因 |
|------|------|:--:|------|
| PortSwigger | Web 安全 | $250-5K | Python 后端, 安全公司 |
| Internet Archive | 数字图书馆 | $100-10K | Go/Python, 开源 |
| Mattermost | 协作平台 | $50-500 | Go, 开源 |
| Supabase | 后端即服务 | $250-3K | Go/TS, 开源 |

## 第二天: 信息收集
```bash
# 1. 读 Scope (最重要!)
# 2. 克隆源码
git clone <repo> /tmp/target
# 3. 运行扫描器
python mcp-scan.py /tmp/target
semgrep --config rules/ /tmp/target
# 4. 手工审关键文件
grep -rn "open\|exec\|shell\|auth\|token\|password" /tmp/target/src
```

## 第三天: 测试
- 用自写 exploit 库里的模式
- 本地 Docker 搭环境验证
- 只测 Scope 内端点

## 第四天: 报告
- 用 standard report template
- 附复现步骤 + PoC 代码
- 提交到 HackerOne

## 预期时间线
| 周 | 产出 |
|:--:|------|
| 第1周 | 提交第一个报告 |
| 第2-4周 | 获得第一个赏金 ($50-500) |
| 第2-3月 | 稳定产出 $500-2000/月 |
