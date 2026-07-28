# Mixin 存储层分析 — BadgerDB + UTXO 持久化

**日期**: 2026-07-30
**源码**: /i/mixin-repos/mixin/storage/

---

## 架构

```
Mixin Kernel
    │
    ├── snapshotsDB (Badger, sync=true)  ← 持久化数据
    │   ├── UTXO, GHOST, DEPOSIT, WITHDRAWAL
    │   ├── MINT, TRANSACTION, FINALIZATION
    │   ├── ROUND, UNIQUE
    │   └── Node, Custodian, Asset
    │
    └── cacheDB (Badger, sync=false)     ← 临时缓存
        └── Graph topology cache
```

## 数据域 (18 个 Key 前缀)

| 前缀 | 存储内容 |
|------|------|
| `GHOST` | 已使用的一次性密钥（防重放） |
| `UTXO` | 未花费输出 + 首次消费交易哈希 |
| `DEPOSIT` | 跨链存款记录 |
| `WITHDRAWAL` | 提现索赔 |
| `MINTUNIVERSAL` | 每日铸币分配 |
| `TRANSACTION` | 原始交易（含最终化快照哈希） |
| `FINALIZATION` | 交易最终化 hack 记录 |
| `UNIQUE` | 每节点唯一交易 |
| `ROUND` | 轮次信息 {node, number, references} |
| 其他 | Assets, Nodes, Custodians, Genesis |

## BadgerDB 配置

| 参数 | 值 | 说明 |
|------|:--:|------|
| 压缩 | None | 牺牲空间换速度 |
| 同步写入 | snapshots=true, cache=false | 持久化数据必须 fsync |
| ValueLog GC | 0.5 阈值 | 日志文件空间回收 |
| 并发 | RWMutex | 读多写少模式 |

## 安全分析

### ✅ 数据一致性

`snapshotsDB` 启用同步写入——每个写操作后调用 `fsync()`，确保崩溃后数据不丢失。

### ✅ 读保护

所有读操作使用 `RLock()`，允许多个并发 goroutine 同时读取——高效且安全。

### ⚠️ 无加密

BadgerDB 数据以明文存储在磁盘上——UTXO 集合、交易历史、节点信息全部可读。如果物理磁盘被盗或 root 权限被获取，所有链上数据暴露。

### ⚠️ 压缩关闭的影响

`Compression: None` 意味着完整 UTXO 集合可能消耗数百 GB 磁盘。Big UTXO 集合（类似 Bitcoin）会成为存储瓶颈。

---

## 评分

| 类别 | 评分 |
|------|:--:|
| 数据一致性 | 8/10 |
| 并发安全 | 8/10 |
| 存储效率 | 5/10 |
| 数据加密 | 2/10 |
| 灾难恢复 | 7/10 |
| **总体** | **6/10** |
