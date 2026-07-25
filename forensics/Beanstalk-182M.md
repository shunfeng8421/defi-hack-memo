# On-Chain Forensics: Beanstalk $182M
## Flash Loan Governance — 13 Seconds to Takeover

**Date**: April 17, 2022  
**Amount**: $182M ($76M + $106M in other assets)  
**Protocol**: Beanstalk — algorithmic stablecoin protocol  
**Root Cause**: Governance token (BEAN) could be flash-loaned  

---

## Attack Flow

```
┌────────────────────────────────────────────────────┐
│ Step 1: Flash Loan BEAN tokens                      │
│ Aave → 350M BEAN (75% of total supply)              │
│ Fee: ~$3,000                                        │
├────────────────────────────────────────────────────┤
│ Step 2: Submit Emergency Governance Proposal         │
│ "Transfer all protocol funds to attacker address"   │
│ Requires 67% voting power                            │
│ Attacker holds: 75%                                  │
├────────────────────────────────────────────────────┤
│ Step 3: Vote YES with 350M BEAN                     │
│ Voting check: balanceOf(attacker) >= quorum          │
│ Flash loan passes the check                         │
├────────────────────────────────────────────────────┤
│ Step 4: Execute Proposal                             │
│ Protocol transfers: $182M to attacker               │
│ Repay flash loan: 350M BEAN                          │
├────────────────────────────────────────────────────┤
│ Step 5: Profit                                       │
│ Net: ~$76M (BEAN value collapsed post-attack)       │
│ Elapsed time: 13 seconds                              │
└────────────────────────────────────────────────────┘
```

## Why Governance Was the Vector

Beanstalk had three security assumptions, all broken:

| Assumption | Why It Failed |
|------|------|
| "Voting requires owning tokens" | Flash loan = own tokens for 1 transaction |
| "67% supermajority is expensive" | Flash loan fee = $3,000 |
| "Emergency proposals would be noticed" | 13 seconds is faster than any human response |

## The Fix

Voting power must be snapshotted at proposal creation time:

```solidity
function propose(...) external {
    proposalSnapshot[proposalId] = block.number;
    // Snapshot balances at this block
}

function getVotes(address account, uint256 proposalId) public view {
    return votes[account][proposalSnapshot[proposalId]];
    // Tokens acquired AFTER proposal creation have ZERO votes
}
```

## Pattern

Pattern #31: Flash Loan Governance Attack — Token-weighted voting + flash-loanable tokens = instant takeover.
