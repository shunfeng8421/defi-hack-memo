# Mixin RPC API 层安全分析

**日期**: 2026-07-30
**源码**: /i/mixin-repos/mixin/rpc/

---

## 架构

```
客户端 ──→ HTTP/:8001 ──→ RPC 路由器 ──→ Store/Kernel
              JSON-RPC       21 方法      查询/提交
```

## 21 个 RPC 方法

| 方法 | 类型 | 鉴权 |
|------|:--:|:--:|
| `getinfo` | 查询 | ❌ 无 |
| `listpeers` | 查询 | ❌ 无 |
| `listrelayers` | 查询 | ❌ 无 |
| `dumpgraphhead` | 查询 | ❌ 无 |
| `sendrawtransaction` | **写入** | ❌ 无 → ✅ Kernel 验证 |
| `gettransaction` | 查询 | ❌ 无 |
| `getcachetransaction` | 查询 | ❌ 无 |
| `getdeposittransaction` | 查询 | ❌ 无 |
| `getwithdrawalclaim` | 查询 | ❌ 无 |
| `getutxo` | 查询 | ❌ 无 |
| `getkey` | 查询 | ❌ 无 |
| `getasset` | 查询 | ❌ 无 |
| `getsnapshot` | 查询 | ❌ 无 |
| `listsnapshots` | 查询 | ❌ 无 |
| `listcustodianupdates` | 查询 | ❌ 无 |
| `listmintworks` | 查询 | ❌ 无 |
| `listmintdistributions` | 查询 | ❌ 无 |
| `listallnodes` | 查询 | ❌ 无 |
| `getroundbynumber` | 查询 | ❌ 无 |
| `getroundbyhash` | 查询 | ❌ 无 |
| `getroundlink` | 查询 | ❌ 无 |

---

## 安全模型

```
RPC 层                Kernel 层
──────                ─────────
无鉴权 ──────────────→ 交易签名验证 (Ed25519)
无速率限制             UTXO 状态验证
6.5KB 请求大小限制      双花检测 (KeyImage)
                      共识规则验证
```

**设计理念**: 类 Bitcoin 节点——RPC 完全公开，安全性完全由 Kernel 层的密码学保证。任何无效交易在 Kernel 层被拒绝，无论谁提交。

---

## 安全分析

### ✅ 设计合理性

Mixin 是有许可共识网络的公链——节点已知且信任，但客户端是公开的。在 P2P 网络层中，节点间有 Ed25519 签名的 AuthToken；但在面向客户端的 HTTP RPC 层，完全开放。这等同于 Bitcoin Core 的 JSON-RPC。

### ✅ 请求大小限制

`maxRPCRequestBodySize = 2 × TransactionMaximumSize + 64KB` —— 防止超大请求耗尽内存。

### ✅ CORS 已配置

```go
w.Header().Set("Access-Control-Allow-Origin", origin)
w.Header().Add("Access-Control-Allow-Headers", "Content-Type,Authorization,Mixin-Conversation-ID")
w.Header().Set("Access-Control-Allow-Methods", "OPTIONS,GET,POST,DELETE")
```

跨域请求已正确配置——Web 钱包可以通过网页直接调用 RPC。

### ⚠️ 无速率限制

没有 IP-based 或 API-key-based 的速率限制。攻击者可以通过 RPC 洪泛无效交易，消耗节点的验证资源。虽然无效交易最终在 Kernel 层被拒绝，但拒绝的成本仍然由节点承担。

### ⚠️ 信息泄露

21 个查询方法返回网络状态的全量数据：
- `listallnodes` + `listpeers` → 完整的节点列表和连接状态
- `dumpgraphhead` → 完整的 DAG 拓扑
- `listsnapshots` → 所有快照历史

这些信息在其他链的节点中通常也是公开的——但全量访问使得链上分析工具可以轻松爬取数据。

### ⚠️ 客户端超时

```go
Timeout: 20 * time.Second
MaxIdleConns: 1024
MaxIdleConnsPerHost: 256
```

20 秒超时和 1024 最大空闲连接——对客户端到节点的普通请求足够，但维护大量空闲连接可能被滥用（连接耗尽攻击）。

---

## 与 Bitcoin Core JSON-RPC 对比

| 特性 | Mixin RPC | Bitcoin Core |
|------|:--:|:--:|
| 传输 | HTTP | HTTP |
| 格式 | JSON-RPC 2.0 | JSON-RPC 1.0 |
| 鉴权 | ❌ 无 | `rpcuser`/`rpcpassword` |
| 方法数 | 21 | 50+ |
| CORS | ✅ | ❌ (default) |
| 速率限制 | ❌ | ❌ |
| 请求大小限制 | ✅ 6.5KB | ✅ 可配置 |

Bitcoin Core 确实有 `rpcuser`/`rpcpassword` 鉴权——但那是为了管理（`sendtoaddress` 等资金操作）。Mixin 的 `sendrawtransaction` 不直接控制资金（交易必须由用户签名），所以不需要鉴权。Mixin 的模型更纯粹地分离了"广播交易"和"控制资金"两个角色。

---

## 评分

| 类别 | 评分 |
|------|:--:|
| API 完整性 | 8/10 |
| 鉴权设计 | 7/10 (区分离线签名，正确) |
| 速率限制 | 3/10 |
| 信息泄露 | 5/10 |
| DoS 抗性 | 5/10 |
| **总体** | **5.5/10** |
