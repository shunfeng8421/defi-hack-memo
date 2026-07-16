# 区块链安全审计 — 完整工作流

## 工具链

```
MCP 安全工厂 → 区块链安全工厂

mcp-scan            → Slither + 自定义检测器
Semgrep 规则        → Slither detectors (flash price, unchecked transfer)
exploit-library     → Foundry PoC 合约
Docker 验证         → anvil fork 主网
reasoner.py         → 业务逻辑推理层
知识图谱            → DeFi 漏洞图谱 (99节点)
```

## 审计流程 (60分钟/合约)

### Phase 1: 自动化扫描 (10分钟)
```
slither . --detect flash-price-oracle,unchecked-transfer-erc20,reentrancy-eth
slither . --print human-summary
```

### Phase 2: 手工审查 (30分钟)
```
1. 读合约概览 + 架构图
2. 检查价格预言机: getReserves() → ❌？
3. 检查重入: checks-effects-interactions？✅？
4. 检查权限: Ownable？多签？时间锁？
5. 检查跨链: chainID？nonce？验证器数？
6. 检查闪电贷: 关键路径是否可被一个交易操纵？
```

### Phase 3: PoC 验证 (15分钟)
```
forge test --match-test test_exploit -vvv  (如果 Foundry 可用)
或: 手动追踪攻击链
```

### Phase 4: 报告 (5分钟)
```
漏洞类型 | 严重性 | 影响 | 修复
闪贷+价格操纵 | CRITICAL | 可提取全部资金 | TWAP
```

## 优先级规则

| 优先级 | 类型 | 例子 |
|:--:|------|------|
| 🔴 | 资金直接损失 | 闪贷+价格操纵 |
| 🟡 | 权限漏洞 | 治理攻击 |
| 🔵 | 信息泄露 | storage 碰撞 |

## 你的差距

| 你有 | 你需要 |
|------|------|
| MCP 审计方法论 ✅ | DeFi 业务深入理解 ⚠️ |
| Solidity 33 模式 ✅ | 实战经验 ⚠️ |
| Slither ✅ | Foundry ❌ (Windows) |
| 知识图谱 99 节点 ✅ | 区块链图谱用例 ❌ |
