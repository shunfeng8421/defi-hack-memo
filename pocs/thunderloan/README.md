# ThunderLoan — Flash Loan Oracle Manipulation
- Severity: 🔴 CRITICAL
- Pattern: #1 — Flash Loan + Price Oracle
- Root: OracleUpgradeable.getPriceInWeth() uses TSwap spot price
- Fix: Replace with 30-min TWAP
- Real-world: bZx $50M, Cream $130M
