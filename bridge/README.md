# 最小跨链桥——攻防教学

## 4 个跨链桥经典漏洞

| # | 漏洞 | 真实案例 | 损失 |
|:--:|------|------|--:|
| 1 | 签名无 nonce | Poly Network | $610M |
| 2 | 签名无 chainId | Nomad Bridge | $152M |
| 3 | 签名无 deadline | 通用 | - |
| 4 | CEI 重入 | 各类桥 | - |

## 合约架构

```
bridge/
├── vulnerable/MinimalBridge.sol  ← 含全部4个bug
├── exploit/Exploit.sol           ← 攻击PoC
├── fixed/FixedBridge.sol         ← EIP-712 + nonce + deadline + ReentrancyGuard
└── BridgeTest.t.sol              ← Foundry 测试
```

## 运行

```bash
forge test --match-path "**/bridge/**" -vvv
```

## 修复清单

- [x] EIP-712 签名 → chainId 自动包含
- [x] nonce 防重放
- [x] deadline 防过期
- [x] ReentrancyGuard 防重入
- [x] 两步转移 + 时间锁
