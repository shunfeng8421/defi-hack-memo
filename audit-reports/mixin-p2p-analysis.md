# Mixin P2P 网络层安全分析

**日期**: 2026-07-30
**源码**: /i/mixin-repos/mixin/p2p/
**语言**: Go + QUIC

---

## 架构

```
外部客户端 ──→ RPC (HTTP) ──→ Kernel
                                 │
节点间通信: QUIC (HTTP/3) ───↕─── 其他 Node
   传输层: Ed25519 自签名 TLS 证书
   认证:   AuthToken (PeerId + Timestamp + Ed25519 签名)
   单流:   MaxIncomingStreams = 1/peer
```

---

## 消息类型 (18 种)

| 类型 | ID | 用途 |
|------|:--:|------|
| Ping | 1 | 未使用（图谱同步已足够活跃） |
| Authentication | 3 | Ed25519 签名握手 |
| Graph | 4 | DAG 拓扑同步 |
| SnapshotConfirm | 5 | 快照确认 |
| TransactionRequest | 6 | 请求特定交易 |
| Transaction | 7 | 单笔交易广播 |
| TransactionBundle | 8 | 批量交易 |
| FinalizedTransactionBundle | 9 | 已最终化的交易包 |
| PreCommitments | 15 | 预先提交（加速下一轮） |
| BatchSnapshotAnnouncement | 20 | Leader 广播快照 |
| BatchSnapshotCommitment | 21 | 节点提交 Ri |
| BatchTransactionChallenge | 22 | Leader 发送聚合 R + 掩码 Z |
| BatchSnapshotResponse | 23 | 节点发送响应 si = ri + H(R||A||M)ai |
| BatchFullChallenge | 24 | 直接全量挑战（有预提交时） |
| BatchSnapshotFinalization | 25 | Leader 聚合签名→最终化 |
| Relay | 200 | 中继消息 |
| Consumers | 201 | 客户端/轻节点消息 |

---

## 批量共识协议（4 步）

借鉴 Ed25519 的 Schnorr 多重签名：

```
Leader                         Node
  │                              │
  ├── Announcement (快照数据) ──→│  1. Leader 广播快照
  │                              │  2. Node 生成随机数 ri, 计算 Ri = ri*G
  │←── Commitment (Ri) ────────┤     发送 Ri
  │                              │
  │  3. Leader 聚合所有 Ri → R    │
  │     生成随机掩码 Z            │
  │     计算挑战: A = f(snapshot) │
  │                              │
  ├── Challenge (R, Z, A) ─────→│  4. Node 验证
  │                              │     计算 si = ri + H(R||A||M)*ai
  │←── Response (si) ──────────┤
  │                              │
  │  5. Leader 验证 si*G = Ri + H(R||A||M)*Ai
  │     聚合所有 si → s           │
  │     Sig = (R, s)              │
  │     finalize if |sigs| ≥ threshold │
  │                              │
  ├── Finalization ────────────→│
```

**安全保证**:
- 每个节点必须知道: ri (随机数) + ai (私钥) 才可签名
- Leader 无法伪造签名: si*G = Ri + H(...)*Ai 必须成立
- 阈值控制: 只有 ≥ 2n/3+1 响应时才能最终化

---

## 安全分析

### ✅ 传输层

- QUIC 天然抗 DDoS（0-RTT 握手，连接迁移）
- Ed25519 自签名证书（无需 CA）
- MaxIncomingStreams=1 限制每个对等方只能有一个双向流——防止资源耗尽

### ⚠️ 时间同步依赖

`AuthToken.Timestamp` 是 10 秒内有效的——要求节点时钟同步。严重的时间偏移可能导致：
- 合法认证被拒绝 → 节点被隔离
- 旧消息重放攻击（如果 Timestamp 精度不够）

### ⚠️ 中继信任模型

中继节点（Relayer，消息类型 200）可以看到经过它们的所有消息内容——即使消息是加密的（因为中继需要路由信息）。中继节点可以：
- 选择性地丢弃消息（DoS）
- 延迟关键快照（拖慢共识）
- 但无法伪造消息（Ed25519 签名验证）

### ⚠️ 已知 Bug

```
// FIXME this could result in a very small topology due to already removed node
// and sync to neighbor since this offset will take substantial time
```

拓扑同步可能因为已移除节点产生过于狭窄的视图——新节点可能需要更长时间与全网同步。

### ✅ DoS 防护

| 机制 | 值 |
|------|:--:|
| 握手超时 | 10 秒 |
| 空闲超时 | 60 秒 |
| 最大流数 | 1/peer |
| 接收超时 | 基于 `time.After` |

---

## 与 libp2p 对比

| 特性 | Mixin P2P | libp2p |
|------|:--:|:--:|
| 传输协议 | QUIC | TCP/QUIC/WebRTC |
| 节点身份 | Ed25519 自签名 | PeerID (多种密钥) |
| 消息格式 | 自定义二进制 | Protobuf |
| 中继 | 自建 Relay 协议 | Circuit Relay v2 |
| NAT 穿透 | 依赖中继 | AutoNAT + Hole Punching |
| 发现 | 图谱同步 + 种子节点 | Kademlia DHT + mDNS |

Mixin 的 P2P 层是自研的最小化实现——只满足 BFT-DAG 共识的需求，牺牲灵活性换取简单性。

---

## 评分

| 类别 | 评分 |
|------|:--:|
| 传输安全 | 8/10 |
| 认证机制 | 7/10 |
| DoS 防护 | 6/10 |
| 中继安全 | 5/10 |
| 网络韧性 | 7/10 |
| **总体** | **6.5/10** |
