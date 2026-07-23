# 🔐 Safe AI Agent Wallet

**全球首个内置安全防护的 AI Agent 钱包**

## 问题

Swapper Finance (⭐827) 让 AI Agent 能交易，但 0 层安全防护。AI Agent 私钥被窃 = 钱包清空。

## 解决方案

Safe AI Wallet 在 AI Agent 和资金之间插入 6 层防护：

| # | 防护 | 拦截什么 |
|:--:|------|------|
| 1 | 工具白名单 | 恶意 `drain` 工具被拦截 |
| 2 | 单笔上限 | 超过 1 ETH 单笔交易被拒绝 |
| 3 | 每日限额 | 累计超 10 ETH 自动停 |
| 4 | 合约白名单 | 只在信任合约上操作 |
| 5 | 大额人类确认 | 2+ ETH 必须人类点同意 |
| 6 | Agent 身份验证 | 过期/撤销的 Agent 无法操作 |

## 快速开始

```bash
python demos/ai-wallet-demo.py
```

## 合约部署

```solidity
// Solidity 版本在 pocs/safe-ai-wallet/SafeAIAgentWallet.sol
// 225行, 8层防护, Foundry测试齐全
```

## 对比

| | Swapper | Safe Wallet |
|------|:--:|:--:|
| ⭐ | 827 | - |
| AI 能交易 | ✅ | ✅ |
| 安全防护 | 0 层 | 6 层 |
| 工具白名单 | ❌ | ✅ |
| 每日限额 | ❌ | ✅ |
| 人类确认 | ❌ | ✅ |

## 作者

Shiqiang Chen · github.com/shunfeng8421/defi-hack-memo
