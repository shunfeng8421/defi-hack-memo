# Audit Report: vault-core — ERC-4626 Inflation Attack

**Auditor**: Shiqiang Chen | **Date**: July 16, 2026
**Project**: TobyDunn/vault-core | **Commit**: main branch
**Severity**: 🔴 **HIGH**

---

## Summary

The `Vault.sol` contract is vulnerable to the classic ERC-4626 inflation attack (Pattern #5 in our 50-pattern classification). The contract lacks protections against share value manipulation through direct token donations.

## Vulnerability Details

### Root Cause

```solidity
// Vault.sol line 126-128
function convertToShares(uint256 assets) public view returns (uint256) {
    return ShareMath.convertToShares(assets, totalSupply, totalAssets());
}

// ShareMath.sol line 20-21: NO protection when totalSupply==0
if (totalSupply == 0 || totalAssets == 0) {
    return assets; // 1:1 first deposit
}
```

No minimum initial deposit, no dead shares, no totalAssets/totalSupply ratio check.

### Attack Path

```
1. Attacker: deposit(1 wei) → 1 share
2. Attacker: asset.transfer(vault, 1000e18) → direct donation
3. totalAssets = 1001e18, totalSupply = 1
4. Victim: deposit(1000e18) → 1000e18*1/1001e18 = 0 shares → revert
5. Attacker: redeem(1) → 1001e18 tokens (100% of vault)
```

### Impact

- Attacker gains proportional share dominance through direct donations
- Subsequent depositors get 0 shares (divide by zero effectively)
- Vault becomes unusable for honest users
- All deposited funds accessible by attacker's single share

### Fix

```solidity
// Option 1: Dead shares on deployment
uint256 constant MIN_LIQUIDITY = 1e3;
constructor() {
    _mint(address(0), MIN_LIQUIDITY); // burned shares
}

// Option 2: Min deposit
function deposit(uint256 assets, address receiver) {
    require(totalSupply == 0 || assets >= minDeposit());
}
```

## Discovery Method

Found using the 50-pattern DeFi vulnerability scan map, specifically **Pattern #5: ERC-4626 Inflation Attack**.

## References

- OZ ERC-4626: https://docs.openzeppelin.com/contracts/5.x/erc4626#inflation-attack
- DEFI-05 in solidity-patterns-50.md
