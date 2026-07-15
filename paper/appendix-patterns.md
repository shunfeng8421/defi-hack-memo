# 50-Pattern Empirical Classification System — Appendix

## Pattern → Code Detection → Real Exploit Mapping

### P1: Flash Loan + Price Oracle Manipulation
```solidity
// ❌ VULNERABLE: Instantaneous AMM price
function getPrice() view returns (uint) {
    return pool.getReserves(); // flash-loanable!
}
// ✅ FIXED: TWAP oracle
function getPrice() view returns (uint) {
    return twapOracle.consult(asset, 1e18);
}
```
**Real cases**: bZx, Harvest Finance, PancakeBunny, BurgerSwap, Beluga, Makina
**Detection**: `amms.getReserves()` → Slither detector: `flash-price-oracle`

### P2: Reentrancy (CEI Violation)
```solidity
// ❌ VULNERABLE: Transfer before state update
function withdraw(uint a) external {
    (bool ok,) = msg.sender.call{value:a}("");
    balances[msg.sender] -= a;
}
// ✅ FIXED: checks-effects-interactions
function withdraw(uint a) external {
    balances[msg.sender] -= a;
    (bool ok,) = msg.sender.call{value:a}("");
}
```
**Real cases**: The DAO, LendfMe, Cream, BurgerSwap
**Detection**: `ReentrancyGuard` inherited? → Slither: `reentrancy-eth`

### P3-P50: Full appendix in repo
See `patterns/` directory at https://github.com/shunfeng8421/defi-hack-memo

---

## Expanded Ground-Truth Labels (50+ verified)

| # | Project | Year | Loss | Category | Source |
|:--:|------|:--:|:--:|------|------|
| 1 | The DAO | 2016 | $60M | 重入 | Multiple post-mortems |
| 2 | Parity First Hack | 2017 | $30M ETH | 权限漏洞 | Parity blog |
| 3 | Parity Kill | 2017 | $280M | 权限漏洞 | Parity blog |
| 4 | BEC Overflow | 2018 | $1.5B* | 整数溢出 | SECBIT analysis |
| 5 | SmartMesh SMT | 2018 | $140M | 精度损失 | Peckshield |
| 6 | SpankChain | 2018 | $155 | 整数溢出 | Post-mortem |
| 7 | LendfMe | 2020 | $25M | 重入 | Peckshield |
| 8 | bZx Flash | 2020 | $50M | 闪贷+操纵 | 1inch analysis |
| 9 | Harvest Finance | 2020 | $25M | 闪贷+操纵 | Harvest post-mortem |
| 10 | Pickle Finance | 2020 | $20M DAI | 闪贷+操纵 | Pickle blog |
| 11 | Cover Protocol | 2020 | $1M | 精度 | Cover analysis |
| 12 | Yearn yDAI | 2021 | $11M | 闪贷+操纵 | Yearn disclosure |
| 13 | Spartan Protocol | 2021 | $30M | AMM 操纵 | Spartan analysis |
| 14 | JulSwap | 2021 | $1.5M | 闪贷+操纵 | SlowMist |
| 15 | BurgerSwap | 2021 | $7M | 闪贷+重入 | SlowMist |
| 16 | PancakeBunny | 2021 | $45M | 闪贷+操纵 | SlowMist |
| 17 | bEarn | 2021 | $11M | 闪贷+操纵 | SlowMist |
| 18 | Belt Finance | 2021 | $6M | 闪贷+操纵 | SlowMist |
| 19 | Cream Finance | 2021 | $130M | 闪贷+重入 | Cream disclosure |
| 20 | Poly Network | 2021 | $610M | 权限漏洞 | SlowMist |
| 21 | Popsicle Finance | 2021 | $20M | AMM 操纵 | SlowMist |
| 22 | Uranium Finance | 2021 | $50M | 精度损失 | SlowMist |
| 23 | Wormhole | 2022 | $320M | 跨链签名 | CertiK |
| 24 | Nomad Bridge | 2022 | $152M | 跨链 | CertiK |
| 25 | BSC Bridge | 2022 | $570M | 签名伪造 | SlowMist |
| 26 | Beanstalk | 2022 | $76M | 闪电贷+治理 | Beanstalk report |
| 27 | Mango Markets | 2022 | $100M | 闪贷+操纵 | CertiK |
| 28 | Euler Finance | 2023 | $197M | 借贷清算 | Euler disclosure |
| 29 | BonqDAO | 2023 | $88M | 闪贷+操纵 | SlowMist |
| 30 | Platypus (Feb) | 2023 | $2M | 闪贷+操纵 | SlowMist |
| 31 | Platypus (Mar) | 2023 | $2M | 闪贷+操纵 | SlowMist |
| 32 | KyberSwap | 2023 | $48M | AMM 操纵 | Kyber analysis |
| 33 | Curve/Vyper | 2023 | $70M | 其他(编译器) | Vyper disclosure |
| 34 | Exactly Protocol | 2023 | $7M | 闪贷+操纵 | SlowMist |
| 35 | Orbit Chain | 2024 | $81M | 跨链 | SlowMist |
| 36 | Hedgey Finance | 2024 | $48M | 签名绕过 | SlowMist |
| 37 | Prisma Finance | 2024 | $12M | 闪贷+操纵 | SlowMist |
| 38 | Lifiprotocol | 2024 | $10M | 闪贷+操纵 | SlowMist |
| 39 | OneInch Settlement | 2025 | $4.5M | MEV/抢跑 | 1inch analysis |
| 40 | Bybit | 2025 | $1.5B | 代理/权限 | Multiple reports |
| 41 | Balancer V2 | 2025 | $120M | 闪贷+操纵 | Balancer disclosure |
| 42 | Cork protocol | 2025 | $12M | 闪贷+操纵 | SlowMist |
| 43 | Silo Finance | 2025 | $500K | 借贷清算 | Silo analysis |
| 44 | Impermax V3 | 2025 | $300K | 闪贷+操纵 | SlowMist |
| 45 | Makina | 2026 | $5.1M | 闪贷+操纵 | CertiK |
| 46 | Whalebit Oracle | 2026 | $824K | 闪贷+操纵 | CertiK |
| 47 | Futureswap | 2026 | $394K | 精度损失 | CertiK |
| 48 | Moonwell | 2026 | $1.78M | 闪贷+操纵 | SlowMist |
| 49 | Truebit | 2026 | $8.5K ETH | 精度损失 | Community |
| 50 | AIXBT Forced Swap | 2025 | $13K | 闪贷+操纵 | BaseScan |
