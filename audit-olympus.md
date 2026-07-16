# Olympus BondingCalculator — Flash Loan Oracle Manipulation

## Description
The `StandardBondingCalculator.valuation()` function uses Uniswap V2 `getReserves()` to determine LP token value. This instantaneous AMM price can be manipulated via flash loans, allowing an authorized depositor to mint excess OHM.

## Vulnerability
```solidity
// StandardBondingCalculator.sol:1-58
function getTotalValue(address _pair) public view returns (uint256 _value) {
    _value = getKValue(_pair).sqrrt().mul(2);
}

function getKValue(address _pair) public view returns (uint256 k_) {
    (uint256 reserve0, uint256 reserve1, ) = IUniswapV2Pair(_pair).getReserves();
    // ⚠️ SPOT PRICE — manipulable via flash loan!
    k_ = reserve0.mul(reserve1).div(10**decimals);
}

function valuation(address _pair, uint256 amount_) external view override returns (uint256 _value) {
    uint256 totalValue = getTotalValue(_pair);
    uint256 totalSupply = IUniswapV2Pair(_pair).totalSupply();
    _value = totalValue.mul(...).div(1e18);
}
```

## Impact
Authorized LIQUIDITYDEPOSITOR can:
1. Flash loan to manipulate Uniswap V2 pool reserves
2. Call `Treasury.deposit(LP, manipulated_amount)` 
3. `tokenValue()` → `valuation()` returns inflated value
4. Mint excess OHM beyond LP's true worth

## Mitigation
Use TWAP oracle instead of spot reserves:
```solidity
function getReserves(address _pair) internal view returns (uint256 r0, uint256 r1) {
    (r0, r1) = IUniswapV2Pair(_pair).getReserves();
    // Replace with TWAP consultation
}
```

## Pattern
DeFi Pattern #1: Flash Loan + Price Oracle Manipulation
