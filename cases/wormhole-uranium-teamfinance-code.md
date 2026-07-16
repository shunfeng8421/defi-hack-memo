# Wormhole $320M — 代码级分析

## 漏洞: Solana端`verify_signatures()`缺少验证者验证

### 链上合约 (Wormhole Solana Program)
```rust
// 伪代码 — Solana program中的错误逻辑
pub fn verify_signatures(
    ctx: Context<VerifySignatures>,
    signers: Vec<[u8; 20]>,   // ⚠️ 签名者地址
    sigs: Vec<Signature>,
    msg: Vec<u8>,
) -> Result<()> {
    // BUG: 只检查签名的数学正确性
    // 不检查 signers 是否来自 guardian set!
    for (signer, sig) in signers.iter().zip(sigs.iter()) {
        verify_ed25519(signer, sig, &msg)?;  // 签名数学通过
        // 但 signer 可能不在 guardian_set 中!
    }
    // 签名数 >= 阈值 → 接受 → mint ETH
    if sigs.len() >= threshold {
        complete_transfer(msg);
    }
}
```

### 攻击执行
1. 任意生成的密钥对 → 签名任意消息
2. 数学验证通过 (因为自己签自己)
3. Guardian set检查被跳过
4. 恶意消息被接受 → 120,000 ETH被mint

### 根本原因

Wormhole在Solana端的signature验证逻辑不完整:
- ✅ 数学验证: `verify_ed25519(signer, sig, msg)` — 签名有效
- ❌ 身份验证: 缺少`guardian_set.contains(signer)` — 签名者可能不是guardian

**模式**: #34 (跨链签名验证缺失)
**防御**: 两级验证 — 数学验证 + 身份验证

---

# Bybit $1.5B — 代码级分析

## 漏洞: 非合约层 — 前端+供应链攻击

### 攻击链 (非Solidity, 而是Web2层面)

```
Safe{Wallet}开发者机器 
  → 被恶意JS注入 
  → Safe前端展示"正常"交易 
  → Bybit团队用Ledger签名 
  → 实际交易修改了代理合约实现地址 
  → 新实现 = 无multisig限制 
  → 401,347 ETH被转走
```

### 合约体现

```solidity
// Bybit冷钱包 — Gnosis Safe Proxy
contract GnosisSafeProxy {
    // 正常流: 通过multisig更新implementation
    fallback() external payable {
        address _impl = implementation; // ← 被修改了!
        assembly { calldatacopy(0, 0, calldatasize()) 
            let result := delegatecall(gas(), _impl, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())
            switch result case 0 { revert(0, returndatasize()) } 
            default { return(0, returndatasize()) }
        }
    }
}

// 攻击者替换的恶意Implementation:
contract MaliciousImpl {
    function transfer(address token, address to, uint256 amount) external {
        IERC20(token).transfer(to, amount); // 无任何权限检查!
    }
}
```

**模式**: #13 (代理升级) + 前端攻击
**防御**: 硬件钱包屏幕确认(Trezor/Ledger必须显示实际calldata); tx模拟

---

# Uranium $50M — 代码级分析

## 漏洞: `swap()` 中储备计算顺序错误

```solidity
function swap(uint256 amountIn) external {
    // ⚠️ BUG: 用当前reserve计算输出
    // 而不是转账后的实际余额!
    uint256 amountOut = (amountIn * reserve1) / (reserve0 + amountIn);
    
    // 转账 (可能失败, 可能少转)
    tokenIn.transferFrom(msg.sender, address(this), amountIn);
    tokenOut.transfer(msg.sender, amountOut);
    
    // reserve更新晚了 — 且用计算值而非实际balance
    reserve0 += amountIn;
    reserve1 -= amountOut;
}
```

### 攻击执行
1. 正常swap → reserve与balance逐渐不同步
2. 反复swap → 累积偏差 → reserve远大于实际balance
3. 最后swap用膨胀的reserve → 抽空池子

**模式**: #7 (AMM储备操纵)
**防御**: 
- 用`balanceOf`更新reserve, 不用`+=`
- swap后立即更新reserve, 用实际值而非计算值

---

# TeamFinance $15.8M — 代码级分析

## 漏洞: 升级删除安全约束

### v2 (安全)
```solidity
contract TeamFinanceV2 {
    function migrate(address token, uint256 amount) external {
        require(amount <= maxMintAmount); // ← 安全约束
        _mint(msg.sender, amount);
    }
}
```

### v3 (不安全)
```solidity
contract TeamFinanceV3 {
    function migrate(address token, uint256 amount) external {
        // ⚠️ maxMintAmount 被删除了!
        _mint(msg.sender, amount);
        // 攻击者调用: migrate(token, type(uint256).max)
        // → 无限铸币 → 耗尽所有流动性
    }
}
```

**模式**: #13 (升级) + 安全回归
**防御**: 
- 升级前后运行不变性检查
- 用模糊测试对比v2和v3的行为差异
- 保留所有安全约束；只添加新功能, 不删除旧检查
