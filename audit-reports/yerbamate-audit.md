# YerbaMate — AI Contract Auditor's Own Contract Has CEI Bug

**Auditor**: Shiqiang Chen | **Date**: July 18, 2026  
**Project**: YerbaMate (AI Smart Contract Audit Agent)  
**Contract**: SimpleVault.sol (46 lines)

## Finding: CEI Violation in withdraw() 

**Severity**: 🔴 CRITICAL  
**AI Attack Vector**: Vector #2 — Cross-Contract Auto-DeFi Chain

### Vulnerable Code

```solidity
function withdraw(uint256 shareAmount) external {
    require(shares[msg.sender] >= shareAmount, "insufficient shares");
    uint256 assets = shareAmount;
    (bool ok, ) = msg.sender.call{value: assets}("");  // ⚠️ EXTERNAL CALL FIRST
    require(ok, "transfer failed");
    shares[msg.sender] -= shareAmount;  // ⚠️ STATE UPDATE AFTER
    totalShares -= shareAmount;
    totalAssets -= assets;
}
```

### Attack

```
1. Attacker deposits 1 ETH → gets 1 share
2. Attacker calls withdraw(1)
3. msg.sender.call{value: 1}("") → triggers attacker's receive()
4. receive() calls withdraw(1) AGAIN → shares still = 1 → passes check
5. Second withdraw(1) → sends ANOTHER 1 ETH
6. Repeats until contract balance = 0
7. shares[attacker] first decremented → but too late
```

### Fix

```solidity
function withdraw(uint256 shareAmount) external {
    require(shares[msg.sender] >= shareAmount, "insufficient shares");
    // CEI: Update state BEFORE external call
    shares[msg.sender] -= shareAmount;
    totalShares -= shareAmount;
    uint256 assets = shareAmount;
    totalAssets -= assets;
    (bool ok, ) = msg.sender.call{value: assets}("");
    require(ok, "transfer failed");
}
```

## Irony

This bug is in the **demo contract of an AI smart contract auditor**. The very tool that's supposed to catch CEI violations ships with one in its own example code. This validates our AI Agent × DeFi research: even AI auditing tools are not immune to the bugs they claim to detect.

---

**AI Agent × DeFi Audit Series**: 5 projects | 13 findings | 6/8 vectors validated
