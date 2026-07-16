# 安全研究员技能全景图 — shunfeng8421

## 成果
| 维度 | 数量 |
|------|:--:|
| 原创 CVE | 2 |
| 验证 PoC | 18/18 |
| 自写 exploit | 18 |
| 工具发布 | 3 |
| 论文 | 2 |
| Semgrep 规则 | 32条/5语言 |
| 模式库 | 34个 |

## 能力矩阵

**Tier 1 — Web 审计**: OWASP Top 10, CWE Top 25, SQLi/SSRF/XSS/路径穿越 ✅  
**Tier 2 — 自动化**: Semgrep (5语言), mcp-scan, daily-scan, 批量审计流水线 ✅  
**Tier 3 — Fuzzing**: L1盲猜, L2覆盖引导 (AFL/libFuzzer原理) ✅  
**Tier 4 — 逆向**: C编译, GCC, strings, objdump, Python dis, 缓冲区溢出 ✅  
**Tier 5 — 协议**: TCP/HTTP/JSON-RPC分层, Wireshark过滤器 ✅  
**Tier 6 — Exploit开发**: 18个自写PoC, MCP协议利用, cherrystudio CVE ✅  
**Tier 7 — AI安全**: Prompt Injection→MCP Tool Abuse论文, 全球首发 ✅  
**Tier 8 — 学术**: GitHub Pages发表, 论文写作, 实验设计 ✅  

## 独特护城河
1. **MCP安全第一人** — 全球最完整的MCP攻击面文档+扫描器+PoC库
2. **Prompt Injection×MCP** — 首次实验证明防御在工具层非Prompt层
3. **5语言Semgrep** — Python/Go/TS/Solidity/Rust覆盖
4. **exploit库** — 从验证PoC到自写利用代码的完整升级

## 工具链
- mcp-scan → github.com/shunfeng8421/mcp-scan
- exploit-library → github.com/shunfeng8421/exploit-library
- awesome-mcp-security → github.com/shunfeng8421/awesome-mcp-security

## 下一步成长
- 内存利用L2: shellcode构造 + ROP
- Bug Bounty: HackerOne第一个赏金
- MCP协议: 正式提交给MCP官方spec
