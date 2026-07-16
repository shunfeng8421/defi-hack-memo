# DeFi 核心漏洞 — 第 1 批实战

## 模式 1: 闪电贷 + 价格操纵

### 原理

```
攻击者:
1. 闪电贷借出 1000 万 USDC (无抵押, 同一交易内归还)
2. 用 1000 万 USDC 在 A 池 swap → 价格暴跌
3. 被攻击合约调用了 A 池的瞬时价格以为资产贬值了
4. 攻击者以"低估"的价格买入 → 套利
5. 归还闪电贷
```

### 漏洞代码

```solidity
// ❌ VULNERABLE: 使用瞬时价格
function getCollateralValue(address token, uint amount) public view returns (uint) {
    (uint reserve0, uint reserve1) = pool.getReserves();  // 可被闪电贷操纵
    uint price = reserve1 * 1e18 / reserve0;
    return amount * price / 1e18;
}
```

### 修复

```solidity
// ✅ FIXED: 使用 TWAP
function getCollateralValue(address token, uint amount) public view returns (uint) {
    uint price = twapOracle.consult(token, 1e18);  // 时间加权 -> 不可闪电贷操纵
    return amount * price / 1e18;
}
```

### 实战测试 (Foundry)

```bash
forge test --match-test test_flash_loan_price_manipulation -vvv
```

---

## 模式 2: 重入 + 闪电贷组合

### 原理

```
1. 闪电贷借出 ETH
2. 攻击合约实现 fallback()
3. 调用 withdraw() → 合约转账 ETH → 触发 fallback()
4. fallback() 再次调用 withdraw() → 余额未更新 → 重复提现
5. 归还闪电贷
```

### 漏洞代码

```solidity
// ❌ VULNERABLE: 先转账后更新余额
function withdraw(uint amount) external {
    require(balances[msg.sender] >= amount);
    (bool ok, ) = msg.sender.call{value: amount}("");  // 转账 → 可能触发重入
    balances[msg.sender] -= amount;  // 余额更新在转账之后!
}
```

### 修复

```solidity
// ✅ FIXED: checks-effects-interactions 模式
function withdraw(uint amount) external {
    require(balances[msg.sender] >= amount);
    balances[msg.sender] -= amount;  // 先更新余额
    (bool ok, ) = msg.sender.call{value: amount}("");  // 后转账
    require(ok);
}
```

---

## 模式 3: TWAP 预言机操纵

### 为什么 TWAP 比瞬时安全

```
瞬时价格: 一个区块内可被大幅操纵
TWAP: 取 N 个区块的平均值 → 操纵成本 = N × 闪电贷成本

攻击者要操纵 TWAP 需要:
- 连续 N 个区块操纵价格
- 每个区块都要支付手续费 + 滑点
- 成本极高 → 经济上不可行
```

### 检查清单

- [ ] 合约使用 `pool.getReserves()` 还是 `oracle.consult()`？
- [ ] TWAP 周期是否足够长？（<30 分钟 = 可能不够）
- [ ] 价格是否用于关键操作？（清算/借贷/铸币）

---

## 模式 4: 滑点保护不足

### 漏洞

```solidity
// ❌ VULNERABLE: 无滑点保护
function swap(uint amountIn, address tokenIn) external {
    uint amountOut = getAmountOut(amountIn, tokenIn);
    pool.swap(tokenIn, amountIn, amountOut);
}
```

攻击者可以在你的交易前面插入一个交易(三明治) → 你得到的价格远低于预期。

### 修复

```solidity
// ✅ FIXED: 最小输出检查
function swap(uint amountIn, address tokenIn, uint minAmountOut) external {
    uint amountOut = getAmountOut(amountIn, tokenIn);
    require(amountOut >= minAmountOut, "滑点保护");
    pool.swap(tokenIn, amountIn, amountOut);
}
```

---

## 模式 5: ERC-4626 通胀攻击

### 原理

```
攻击者:
1. 直接向 vault 捐赠少量资产 (donate)
2. 使得 share 精度损失 → 后续小额存款者的 share 归零
3. 下一个存款者存入 → 攻击者以极低成本提取全部

本质: share 计算中的精度丢失
```

### 漏洞

```solidity
function deposit(uint assets) external returns (uint shares) {
    shares = assets * totalSupply() / totalAssets();  // totalAssets 可被人为膨胀
    _mint(msg.sender, shares);
}
```

### 修复

```solidity
function deposit(uint assets) external returns (uint shares) {
    // 如果有精度丢失风险 → 直接铸币给第一个存款者
    if (totalSupply() == 0) {
        shares = assets - OFFSET;  // 预存一个 offset 防止攻击
    } else {
        shares = assets * totalSupply() / totalAssets();
    }
    _mint(msg.sender, shares);
}
```

---

## 实战练习

### 练习 1: 找漏洞

```solidity
contract Lending {
    mapping(address => uint) public deposits;
    
    function deposit() external payable {
        deposits[msg.sender] += msg.value;
    }
    
    function withdraw(uint amount) external {
        require(deposits[msg.sender] >= amount, "余额不足");
        deposits[msg.sender] -= amount;
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "转账失败");
    }
}
```

**问题是什么？** 答案在下面...

```
...思考...
...思考...

答案: 没有重入保护。虽然先减余额再转账(checks-effects-interactions), 
但如果攻击者的 withdraw 函数被外部合约回调 -> 攻击者可以多次调用 withdraw。
实际上这个代码是对的! 因为它用了 checks-effects-interactions。
但如果有其他函数也可以修改 balances, 就可能有问题。
```

### 练习 2

```solidity
contract PriceAware {
    IUniswapV2Pair pool;
    
    function getLTV(address user) public view returns (uint) {
        uint price = pool.getReserves();  // ❌ ???
        return userCollateral * price / userDebt;
    }
}
```

**问题：** 这是闪电贷可操纵的瞬时价格。应用 TWAP 预言机修复。
