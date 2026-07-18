# Tare Protocol — ERC-7540 Deep Attack Analysis

## ERC-7540 核心机制

```
用户                    Vault
 |                       |
 |-- requestDeposit() -->|  异步请求存入
 |<-- requestId ---------|
 |    (等待处理...)       |
 |-- claimDeposit() ---->|  认领份额
 |<-- shares ------------|
```

**关键**：请求和认领之间有**时间窗口**——价格可能变化。

## 六大攻击向量

### 1. 价格漂移攻击 (Price Drift — CRITICAL)

**机制**：requestDeposit 时快照价格 ≠ claimDeposit 时实际价格

```
攻击者:
  T1: requestDeposit(1000 tokens) → 快照价格 = $1/token
  T2: 操纵预言机 → 价格 = $0.5/token
  T3: claimDeposit() → 1000 × $1/$0.5 = 2000 shares (双倍!)
  T4: requestRedeem(2000) → claimRedeem() → 2000 tokens
  利润: 1000 tokens
```

**检测**：
- [ ] 份额计算使用什么价格？
- [ ] 是申请时快照还是认领时实时价？
- [ ] 是否用 TWAP？
- [ ] 有最小等待期吗？

### 2. 认领顺序攻击 (Claim Ordering — HIGH)

**机制**：多个挂起请求，先认领的人拿更多

```
池中有 100 tokens pending:
  用户A: requestDeposit(50) → 挂起
  用户B: requestDeposit(50) → 挂起
  此时仅 100 tokens 可用
  
  用户A claimDeposit() → 拿走 100 tokens (全拿!)
  用户B claimDeposit() → 0 tokens → revert/永久挂起
```

**检测**：
- [ ] claim 是否按 FIFO 顺序？
- [ ] 是否有 maxPendingRequests 限制？
- [ ] 部分认领是否允许？

### 3. 预言机操纵 (Oracle — CRITICAL)

**检测**：
- [ ] 价格来源 = Chainlink？Uniswap V2/V3？自定义？
- [ ] 如果是 AMM：用 getReserves() 还是 consult()？
- [ ] TWAP 窗口 ≥ 30 分钟？
- [ ] 有价格偏差检查（deviation check）吗？
- [ ] 闪贷可瞬时操纵吗？

### 4. 请求取消竞态 (Cancel Race — MEDIUM)

```
用户: requestDeposit(100 ETH)
管理员: 看到此交易 → 暂停合约 → 价格已变
用户: claimDeposit() → revert（合约暂停）
用户: 想 cancel → 但 cancel 也需要合约未暂停
结果: 资金被卡住
```

**检测**：
- [ ] cancel 在 paused 状态下是否可用？
- [ ] 取消是否有时间限制？
- [ ] 管理员能否拒绝特定请求？

### 5. NFT 所有权冲突 (NFT Ownership — HIGH)

Tare 使用 asset-level NFT 表示贷款。常见问题：

```
NFT 代表贷款 A(ETH 抵押品)
  用户质押 ETH → mint NFT → 转移 NFT 给其他人
  问题: 谁有权赎回抵押品？NFT 持有者还是原始存款人？
  
  如果 NFT 持有者可以赎回 → 没问题
  如果原始存款人可以赎回 → 双重索赔!
```

**检测**：
- [ ] 抵押品赎回权绑定在 NFT 还是原始地址？
- [ ] NFT transfer 时是否更新内部记账？
- [ ] 是否存在"贷款已还但 NFT 存在"的状态？

### 6. 双边记账漂移 (Double-Entry Drift — MEDIUM)

Tare 声称使用双边记账。常见 bug：

```
借贷方 ≠ 贷方
  借出: 1000 USDC → 借出记账 +1000
  收回: 800 USDC + 200 USDC 利息 → 收回记账 -1000
  但实际收到 800+200=1000? 还是 800?
  如果记账错误: 借贷方 1000, 贷方 800 → 200 差异永久丢失
```

**检测**：
- [ ] 每个操作后 totalAssets = sum(all positions)？
- [ ] 利息计算是否独立验证？
- [ ] 是否存在 rounding 累积？

## 审计清单

### 第一遍：架构理解 (30 分钟)
- [ ] 数合约，画依赖图
- [ ] 识别入口函数（deposit/redeem/borrow/repay）
- [ ] 找到预言机合约
- [ ] 找到权限管理合约

### 第二遍：扫描器运行 (5 分钟)
```bash
python defi-scanner.py <tare-repo>/src/
```

### 第三遍：手动审计（重点区域）
- [ ] ERC-7540 请求/认领流程逐行审查
- [ ] 预言机价格来源 + 操纵可能性
- [ ] NFT 所有权转移逻辑
- [ ] 权限/管理员函数
- [ ] 利率计算 + rounding

### 第四遍：边界情况
- [ ] 0 金额操作
- [ ] 最大金额操作
- [ ] 暂停/解冻状态
- [ ] 跨合约调用顺序
- [ ] 重入保护

## 预期发现量

基于 824 案例数据，ERC-7540 新标准 + 贷款协议 → 预计 3-5 个中等以上發現。
