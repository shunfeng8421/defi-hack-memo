# Agent Prediction Markets — Full Professional Audit

**Protocol**: Agent Prediction Markets (Base chain)  
**Contracts**: 5 core — 2,028 lines total  
**Auditor**: Shiqiang Chen · July 2026  

---

## Overall Score: 4.5/10 — Multiple Centralization Vectors

---

## Finding #1: adminResolve Backdoor (🔴 CRITICAL)

**File**: OracleResolver.sol:245-269
**Attack**: Owner can unilaterally resolve ANY market regardless of votes.

```solidity
function adminResolve(uint256 marketId, uint256 outcomeId)
    external onlyOwner nonReentrant
{
    resolution.status = ResolutionStatus.Finalized;
    resolution.finalized = true;
    // ... notify market factory ...
}
```

This function has NO requirement that the market is disputed. It can be called on any market at any time. The "decentralized oracle voting system" is a front for owner-controlled outcomes.

**Fix**: Restrict `adminResolve` to only disputed markets (`resolution.status == ResolutionStatus.Disputed`).

---

## Finding #2: Reputation Manipulation (🔴 HIGH)

**File**: OracleResolver.sol:329-334 + 138-140

The owner can:
1. Call `setOracleReputation(ownerAddress, 100)` 
2. Call `proposeResolution()` — auto-votes with full weight
3. Win every single vote unilaterally

**Attack flow**: Same address has both `owner` role AND `trustedOracle` status (constructor at line 103-104). The owner can max out their own reputation and auto-win every resolution.

**Fix**: Prevent owner from being a trusted oracle. Separate the roles.

---

## Finding #3: Trivial Dispute Bond (🟠 MEDIUM)

**File**: OracleResolver.sol:54
**Bond**: 0.0001 ETH ($0.25)

An attacker can spend $25 to dispute 100 resolutions, grinding the entire system to a halt and forcing `adminResolve()` invocation on every single one.

**Fix**: Scale dispute bond with market size. `bond = max(0.1 ether, market.totalBets / 100)`.

---

## Finding #4: Vote Weight Asymmetry (🟠 MEDIUM)

**File**: OracleResolver.sol:159

```solidity
uint256 weight = trustedOracles[msg.sender] ? oracleReputation[msg.sender] : 1;
```

Normal users get weight=1. Oracles get reputation-weighted votes (up to 100x). This creates a small oligarchy that dominates all voting, making the system effectively permissioned despite appearing permissionless.

---

## Comparison: Prediction Market Audit Scores

| Protocol | Overall | Oracle Decentralization | Centralization Risk |
|------|:--:|:--:|:--:|
| Agent Prediction Markets | 4.5/10 | ❌ 2/10 | Owner can override everything |
| Polymarket | 7/10 | Manually resolved | No admin override |
| Augur | 8/10 | Decentralized disputes | REP-weighted |

---

## Recommendation

Add a `TIMELOCKED_ADMIN` role. All `adminResolve` calls must go through the Kleidi-style timelock (7-day delay). This doesn't eliminate the centralization risk but creates a transparency window where users can exit before admin actions take effect.
