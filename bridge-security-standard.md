# Cross-Chain Bridge Security Standard (CBSS) v1.0

**Author**: Shiqiang Chen · Independent Researcher
**Based on**: $3.2B bridge losses (2020-2026), 12 bridge-specific findings, Cherum professional audit

---

## 1. Why Bridges Need Their Own Standard

Bridges are the single largest loss category in DeFi, but no unified security framework exists. Each bridge audit reinvents the wheel. This standard defines a common vocabulary and checklist.

## 2. Six Critical Attack Surfaces

### AS-1: Message Verification Bypass
**Example**: NomadBridge $152M — attacker crafted valid-looking messages
**Check**: Is every incoming message verified against expected format and signer?
**Pattern**: #19 Cross-Chain Replay, #27 EIP-712 errors

### AS-2: Validator Collusion
**Example**: Ronin Bridge $625M — 5/9 validators compromised
**Check**: What is the threshold? 2/3? Majority? Can validators collude?
**Pattern**: #5 ERC-4626 inflation (liquidity side)

### AS-3: Replay Attack
**Example**: giddyvaultv3 $1.3M — EIP-712 TYPEHASH missing fields
**Check**: Does every signed message include chainId + nonce + deadline?
**Pattern**: #19 Cross-Chain Replay

### AS-4: Mint/Burn Asymmetry
**Example**: Wormhole $326M — minted without corresponding burn
**Check**: Is mint() protected by the same validation as burn()?
**Pattern**: #17 Mint/Burn Asymmetry

### AS-5: Upgradeability Attack
**Example**: PolyNetwork $610M — upgraded to malicious implementation
**Check**: Upgrade timelock? Multi-sig requirement? Immutable core logic?
**Pattern**: #13 Admin Key/Privilege Escalation

### AS-6: Timeout/Stuck Funds
**Example**: Cherum parkedUSDC accounting — failed delivery locks funds
**Check**: Is there a recovery path for failed cross-chain deliveries?
**Pattern**: #37 Deposit Lock

## 3. Bridge Security Levels

| Level | Requirements | Examples |
|:--:|------|------|
| **Platinum** | AS1-6 mitigated + formal verification | — |
| **Gold** | AS1-5 mitigated + audit | Cherum (9/10) |
| **Silver** | AS1-4 mitigated | — |
| **Bronze** | AS1 + AS3 mitigated | — |

## 4. Audit Checklist

- [ ] Message format: every field validated?
- [ ] Validator threshold: ≥ 2/3?
- [ ] ChainId in every signed message?
- [ ] Mint/Burn: invariant enforced?
- [ ] Upgrade: timelock + multi-sig?
- [ ] Failed delivery: recovery path exists?

## 5. Reference Audits

| Bridge | Rating | Notes |
|------|:--:|------|
| Cherum | Gold | CCTP V2, EIP-712 co-sign, parkedUSDC |
| VerusBridge | ❌ | Merkle proof forge → $11.6M |
| NomadBridge | ❌ | Message bypass → $152M |
| PolyNetwork | ❌ | Upgrade exploit → $610M |

---

**Repository**: github.com/shunfeng8421/defi-hack-memo
