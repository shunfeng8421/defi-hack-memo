# Chapter 19: RWA Tokenization Risks

*"When a token says 'redeemable for 1 oz gold,' the question is not whether the code is correct. The question is whether the gold exists."*

---

## The Custody Problem

Real-world asset tokenization bridges physical assets to digital tokens. A token representing a US Treasury bond is only as valuable as the legal and operational infrastructure that guarantees redemption. If the custodian holding the bond goes bankrupt, the token becomes worthless—not because the code failed, but because the bridge between the physical and digital worlds collapsed.

This is the fundamental difference between RWA security and pure DeFi security. In DeFi, if the code is correct, the asset is safe. In RWA, the code can be perfect and the asset can still disappear.

---

## Pattern #50: Double-Minting (Fractional Reserve)

**Severity**: CRITICAL

### The Vulnerability

One physical gold bar in a vault. Two GOLD tokens minted on-chain. The custodian—or an attacker who compromises the custodian—mints more tokens than there are physical assets.

### The Fix

On-chain proof-of-reserves updated in real time:

```solidity
function mint(address to, uint256 amount) external onlyCustodian {
    require(
        amount <= totalReserves - totalSupply,
        "Insufficient reserves"
    );
    _mint(to, amount);
}
```

But this only works if `totalReserves` accurately reflects the physical vault. The oracle problem again—the vault's contents must be attested by a trusted party.

---

## Pattern #51: Redemption Failure

**Severity**: CRITICAL

### The Vulnerability

A user holds a token redeemable for a physical asset. The custodian cannot—or will not—deliver the asset. Either the asset was never there (fractional reserve), or legal restrictions prevent delivery (sanctions, bankruptcy).

### The Fix

Bankruptcy-remote trust structures and mandatory insurance. Code cannot fix legal failure modes. Token holders must understand that they hold a claim on a claim, not the underlying asset directly.

---

## Pattern #52: Compliance Bypass via DEX

**Severity**: HIGH

### The Vulnerability

RWA tokens are restricted to KYC-verified addresses via an allowlist. But if the token is listed on a decentralized exchange, anyone can buy it without KYC. The allowlist protects transfers but not trades.

---

*Next: Chapter 20 — GameFi Economics*
