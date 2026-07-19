# 2 More Exploit Findings — Batch 5

## 1. NewMarketTrading $3.98M — Safe Module Malicious Drain

- **Loss**: $3.98M across 88 Gnosis Safes on Ethereum/Base/Arbitrum
- **Date**: May 2026
- **Pattern**: #12 Missing Access Control + Safe Module

### Root Cause

The "SquidRouterModule" was installed on 88 Gnosis Safe multisigs. This module had `delegatecall` to an arbitrary implementation, allowing the attacker to drain all funds. The issue: Safe modules run with Safe's full authority — a malicious module = total control.

### Attack
```
1. Module registered on Safe → has full signing authority
2. Module delegatecalls attacker-controlled implementation
3. Implementation drains all tokens from Safe
4. 88 Safes × 3 chains = $3.98M total
```

---

## 2. TrustedVolumes $5.87M — RFQ Proxy Delegatecall Drain

- **Loss**: $5.87M (1,291 WETH + 206K USDT + 17 WBTC + 1.27M USDC)
- **Date**: May 2026
- **Pattern**: #41 Unsafe Delegatecall + Unlimited Approval

### Root Cause

The RFQ settlement proxy (`0xeEeEEe...`) used **UNVERIFIED bytecode** as its delegatecall implementation. The victim had granted UNLIMITED approval to this proxy. The "allowed order signer" was the attacker.

### Attack
```
1. Victim grants unlimited USDC/WETH approval to proxy
2. Attacker (registered signer) submits malicious order
3. Proxy delegatecalls unverified implementation → tokens transferred
```

---

**Today: 5 new finds | Total: 14 | $64.47M**
