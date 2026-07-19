# 2 More — ThetanutsFi Whitehat + Lixir Permit

## 1. ThetanutsFi $2.1M — Precision Math + Whitehat Rescue

- **Loss**: $2.1M (net ~$100K after $2M whitehat rescue)
- **Date**: June 2026
- **Pattern**: #34 Precision / Vault Share Calculation

### Root Cause
Legacy vault share rounding allowed attacker to mint shares at artificially low prices by manipulating the vault's collateral ratio. A whitehat bot detected the exploit and rescued ~$2M before the attacker could extract all funds.

### Significance
Demonstrates that **MEV bots can be defenders** — the whitehat front-ran the attacker's extraction transaction. This is the opposite of our earlier finding where a MEV bot stole from the makina attacker.

---

## 2. Lixir Permit Drain — Multi-Contract Permit Exploit

- **Loss**: 2.60 ETH + 4,477 USDC + 3,609 USDT + 24,182 LIX
- **Date**: June 2026
- **Pattern**: #15 Permit/Approve Front-running

### Root Cause
6 vulnerable contracts accepted permit signatures without proper validation. The attacker reused valid `permit()` signatures across all 6 contracts, draining tokens from each.

---

**Today: 7 new finds | Total: 16 | $66.67M**
