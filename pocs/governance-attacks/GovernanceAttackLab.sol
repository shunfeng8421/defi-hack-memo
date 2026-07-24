// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Governance Attack Lab — 6 DAO Exploit Patterns
/// @author Shiqiang Chen · July 2026

contract Attack1_FlashLoanGovernance {
    // Attack: Flash loan governance tokens → vote on malicious proposal
    // Real: Beanstalk $182M — flash-loaned 350M BEAN tokens → passed emergency governance
    // Fix: Vote snapshot at proposal creation, not execution
}

contract Attack2_DelegationChain {
    // Attack: Delegate votes through long chain → obscure real voter
    // Voter A → delegates to B → delegates to C → C acts maliciously
    // Fix: Limit delegation depth; timeout stale delegations
}

contract Attack3_TimelockBypass {
    // Attack: Proposal has timelock, but attacker can front-run execution
    // 1. Malicious proposal passes
    // 2. Timelock: 48h delay
    // 3. Attacker front-runs the execution with MEV → steals before timelock ends
    // Fix: Atomic execution; no external calls during governance execution
}

contract Attack4_QuorumManipulation {
    // Attack: Reduce quorum by abstaining or using low-participation periods
    // 1. Wait for low-activity period (holiday, weekend)
    // 2. Submit proposal with low quorum threshold
    // 3. Pass with minimal voting power
    // Fix: Moving-average quorum, not fixed threshold
}

contract Attack5_MultiSigSocialEngineering {
    // Attack: Not technical — social
    // 1. Compromise 1 signer's key
    // 2. Use that signer to approve a "security upgrade"
    // 3. Other signers approve without reading (it happens!)
    // Real: Ronin Bridge $625M — 5/9 keys compromised socially
    // Fix: Hardware wallets + mandatory review period
}

contract Attack6_VoteBuyingMarkets {
    // Attack: Create a market where votes can be openly bought/sold
    // 1. Protocol: $1M bribe pool for "yes" voters
    // 2. Users vote yes → get paid → protocol passes malicious proposal
    // Fix: Secret voting (commit-reveal); quadratic voting
}
