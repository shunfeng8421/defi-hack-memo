// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Optimistic Rollup Security Lab — 6 Fraud Proof Attack Vectors
/// @notice L2 security is assumed. What if it breaks?
/// @author Shiqiang Chen · July 2026

// ============================================================
// The Optimistic Rollup Trust Model
// ============================================================
// Optimistic Rollups assume:
//   1. At least 1 honest verifier exists
//   2. Verifier can post fraud proof within challenge period
//   3. Fraud proof bond > challenge cost
//   4. L1 Sequencer (when enforced) is eventually available
//
// Every assumption is an attack surface.

// ============================================================
// Attack #1: Challenge Period Exhaustion
// ============================================================
contract Attack1_ChallengeExhaustion {
    // VULNERABLE: Fixed challenge period (e.g., 7 days)
    // Attack: Sequencer posts invalid state root → L1 congestion
    // → verifiers can't get transactions confirmed within 7 days
    // → invalid state becomes FINAL
    //
    // Real: This would require sustained L1 congestion for 7 days
    // Mitigation: Dynamic challenge period that extends during
    // L1 congestion (gas price > threshold → extend window)
    //
    // Pattern #70: Challenge Period Denial-of-Service

    uint256 public constant CHALLENGE_PERIOD = 7 days;
    uint256 public constant MAX_CHALLENGE_EXTENSION = 14 days;
    
    function extendIfCongested() external {
        // FIX: If L1 gas price > 10x average, extend challenge window
        if (tx.gasprice > historicalAverageGasPrice * 10) {
            challengePeriodEnd += CHALLENGE_PERIOD;
            if (challengePeriodEnd > block.timestamp + MAX_CHALLENGE_EXTENSION) {
                challengePeriodEnd = block.timestamp + MAX_CHALLENGE_EXTENSION;
            }
        }
    }
}

// ============================================================
// Attack #2: Fraud Proof Bond Arbitrage
// ============================================================
contract Attack2_BondArbitrage {
    // VULNERABLE: Fixed fraud proof bond
    // Attack: Attacker posts invalid state that costs $1M to challenge
    // Bond is $100K → no rational verifier challenges
    // Attacker's expected profit: (value_extracted - bond_lost_if_challenged)
    //
    // If value_of_invalid_state > bond * probability_of_challenge,
    // attack is profitable
    //
    // Fix: Bond scales with value at stake
    // Bond = max(fixed_bond, percentage_of_total_TVL)

    function calculateBond(uint256 totalTVL) internal pure returns (uint256) {
        return max(100 ether, totalTVL / 1000); // 0.1% of TVL floor
    }
}

// ============================================================
// Attack #3: Sequencer Censorship (Pre-EIP-4844)
// ============================================================
contract Attack3_SequencerCensorship {
    // VULNERABLE: Single sequencer can censor transactions
    // Attack: Sequencer refuses to include withdrawal tx
    // → user funds stuck on L2
    //
    // Defense: Enforced L1 inclusion path (EIP-4844 blob space)
    // Users can force-include transactions through L1 after
    // a timeout period, bypassing the sequencer
    //
    // Pattern #71: Sequencer Censorship via L1 Griefing

    uint256 public constant FORCE_INCLUSION_DELAY = 24 hours;
    
    struct ForceInclusion {
        address sender;
        bytes   txData;
        uint256 requestedAt;
    }
    
    mapping(bytes32 => ForceInclusion) public forcedTxs;
    
    function forceInclude(bytes calldata txData) external {
        bytes32 id = keccak256(abi.encodePacked(msg.sender, txData, block.number));
        forcedTxs[id] = ForceInclusion(msg.sender, txData, block.timestamp);
        // After FORCE_INCLUSION_DELAY, any L1 tx can execute this
    }
    
    function executeForced(bytes32 id) external {
        ForceInclusion memory fi = forcedTxs[id];
        require(fi.requestedAt + FORCE_INCLUSION_DELAY <= block.timestamp);
        delete forcedTxs[id];
        // Execute the forced transaction on L1 behalf
    }
}

// ============================================================
// Attack #4: Fraud Proof Verification Bypass
// ============================================================
contract Attack4_ProofVerificationBypass {
    // VULNERABLE: Fraud proof verification has a bug
    // Attack: Attacker finds a valid state transition that
    // the fraud proof verifier incorrectly rejects as invalid
    // → honest transactions are reverted → protocol loses liveness
    //
    // This is the ZK circuit vulnerability (Pattern #54) applied
    // to Optimistic Rollup fraud proof verifiers
    //
    // Real: None known yet — this is a forward-looking concern
    // as fraud proof verifiers grow more complex
}

// ============================================================
// Attack #5: Multi-Round Fraud Proof Griefing
// ============================================================
contract Attack5_MultiRoundGriefing {
    // VULNERABLE: Binary search fraud proofs require multiple rounds
    // Attack: Dishonest proposer forces N rounds of interaction
    // Cost: N * L1 gas per round
    // If N * gas_cost > honest_verifier_budget, verifier gives up
    
    // Mitigation: Single-round fraud proofs (Arbitrum's BOLD protocol)
    // Confirm one step → entire assertion confirmed
    // No multi-round interaction → no griefing possible
}

// ============================================================
// Attack #6: Withdrawal Delay Exploitation
// ============================================================
contract Attack6_WithdrawalDelay {
    // VULNERABLE: Standard 7-day withdrawal delay
    // Attack: Market event causes L2 token price to diverge from L1
    // Users initiate withdrawal → wait 7 days → price moved against them
    //
    // This is not a code vulnerability but a design constraint.
    // Fast withdrawals require third-party liquidity providers
    // (Hop Protocol, Across) who themselves introduce new risks.
    //
    // Pattern #72: Withdrawal Delay Market Divergence
}
