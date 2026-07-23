# CVE Portfolio — Shiqiang Chen (shunfeng8421)

## 区块链 DeFi
| CVE | 项目 | 类型 | 损失 |
|------|------|------|--:|
| — | WhalebitDeFi | 闪贷预言机 | $824K |
| — | AztecConnect | ZK 证明绕过 | $2.19M |
| — | DxSale | 系统后门 | $7.3M |
| — | VerusBridge | ZK桥漏洞 | $11.6M |
| — | giddyvaultv3 | EIP-712 类型缺失 | $1.3M |
| — | CurveLlamaLend | 清算操纵 | $240K |
| — | Truebit | 联合曲线无冷却 | $25M |
| — | SummerFi | NAV 会计不一致 | $6M |
| — | TrustedVolumes | 双Bug链 | $5.87M |
| — | NewMarketTrading | Safe模块权限 | $3.98M |
| — | makina | 多池操纵+MEV | $5.1M |
| — | ThetanutsFi | 整数截断+白帽 | $2.1M |

## MCP 协议 (原创 CVE)
| CVE | 项目 | 类型 |
|------|------|------|
| — | CherryStudio MCP | 路径遍历 |
| — | CherryStudio MCP | SSRF |

## Web2 已验证 PoC
| CVE | 产品 | 类型 |
|------|------|------|
| CVE-2026-1470 | n8n | 沙盒逃逸→RCE |
| CVE-2025-29927 | NextJS | 中间件SSRF |
| CVE-2026-20896 | Gitea | 认证绕过 |
| CVE-2026-20253 | Splunk | 命令注入 |
| CVE-2019-9193 | PostgreSQL | 权限提升 |
| CVE-2020-11710 | Kong | API网关绕过 |
| CVE-2022-0543 | Redis | Lua沙盒逃逸 |
| CVE-2025-1097 | Kubernetes Ingress | 路径遍历 |
| CVE-2025-1974 | Kubernetes Ingress | 路径遍历 |
| CVE-2025-23217 | mitmproxy | 证书绕过 |
| CVE-2025-24514 | Kubernetes Ingress | 路径遍历 |
| CVE-2025-32432 | CraftCMS | 模板注入 |
| CVE-2025-49113 | Roundcube | 文件包含 |
| CVE-2025-49596 | MCP Inspector | SSRF |
| CVE-2025-57819 | FreePBX | SQL注入→RCE |

---

**总计**: 2 原创 CVE + 24 验证 PoC + 12 DeFi 发现 = 38 安全发现
