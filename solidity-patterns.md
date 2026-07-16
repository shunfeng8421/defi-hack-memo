### W16: 预言机数据过时 — 无 freshness 检查

```
Chainlink latestAnswer() → 已弃用 → 没有时间戳
攻击: 预言机停止更新 → 价格不变 → 以过时价格清算/借贷
```

**真实案例**: 
- exactly/protocol #811 (你发现的) — `latestAnswer()` 无 staleness 检查
- Cream Finance $130M — 预言机操纵

**搜法**: `latestAnswer()` 调用无 `latestTimestamp()` 或 `updatedAt` 检查

**修复**: 
```solidity
(, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();
require(updatedAt >= block.timestamp - STALE_THRESHOLD, "stale price");
```

### W17: 捐赠清算攻击

```
攻击者: 直接向策略合约发送 token（捐赠）
策略: totalAssets() 计算时包含了捐赠 → 每股净值被稀释/膨胀
其他用户: 赎回时得到错误的金额
```

**修复**: 用内部会计追踪真实存入量，不用 `balanceOf(this)`

### W18: 舍入方向错误

```
协议: 用户提款 100 USDC → 计算份额 = 99.9999 → 向下取整 = 99 → 用户损失 1 USDC
或: 用户存款 → 向上取整 → 用户多付
```

**修复**: 存款向上取整（对协议有利），提款向下取整（对协议有利）——方向不能反
