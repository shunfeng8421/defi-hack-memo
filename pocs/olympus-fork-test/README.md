# Olympus Oracle Manipulation PoC

## 漏洞
StandardBondingCalculator.valuation() 使用 UniswapV2Pair.getReserves() 瞬时价格——可被闪贷操纵。

## 攻击链

```
闪贷 10M DAI → 换成 OHM → OHM-DAI 池储备失调
→ BondingCalculator 返回膨胀 LP 价值
→ Treasury.deposit(LP) 铸造超额 OHM
→ 卖出 OHM → 还闪贷 → 利润
```

## 运行

```bash
# 需要有主网RPC (Alchemy/Infura)
forge test --fork-url $ETH_RPC -vvv
```

## 代码证据

StandardBondingCalculator.sol:39-43
```solidity
function valuation(address _pair, uint256 amount_) external view returns (uint256) {
    uint256 totalValue = getTotalValue(_pair);  // ← getKValue().sqrrt()
    uint256 totalSupply = IUniswapV2Pair(_pair).totalSupply();
    return totalValue.mul(...).div(1e18);
}

function getKValue(address _pair) public view returns (uint256) {
    (uint256 reserve0, uint256 reserve1,) = IUniswapV2Pair(_pair).getReserves(); // ⚠️ SPOT
    k_ = reserve0.mul(reserve1).div(10**decimals);
}
```

Treasury.sol:480-485
```solidity
function tokenValue(address _token, uint256 _amount) public view returns (uint256) {
    value_ = _amount.mul(...).div(...); // decimal normalization
    if (permissions[LIQUIDITYTOKEN][_token]) {
        value_ = IBondingCalculator(bondCalculator[_token]).valuation(_token, _amount); // ⚠️ exploit path
    }
}
```

## 缓解
- 用 TWAP 替代 getReserves()
- LIQUIDITYDEPOSITOR 权限审计
- 铸币量上限 (per-block cap)
