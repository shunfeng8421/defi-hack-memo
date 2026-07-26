// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Intent Architecture Security Lab — 6 Solver/Filler Attack Vectors
/// @notice "I want to swap 10 ETH for USDC at best price" — who executes this and how?
/// @author Shiqiang Chen · July 2026

// ============================================================
// The Intent Paradigm
// ============================================================
// Traditional DEX: User specifies exact execution path → tx executes
// Intent-based: User signs "I want X output for Y input" → solver
// competes to provide best execution. The solver CHOOSES the path.
//
// Power shifts from the user to the solver. Every solver is a
// potential attacker — they have private order flow, MEV access,
// and the ability to choose execution timing and routing.

// ============================================================
// Attack #1: Solver Collusion (Price Fixing)
// ============================================================
contract Attack1_SolverCollusion {
    // VULNERABLE: Solvers compete in an auction for order flow
    // Attack: Dominant solvers agree to split orders and not undercut
    // each other → users always get the collusion price, not the
    // competitive price. This is identical to traditional finance
    // market maker collusion — just with smart contracts.
    //
    // Real concern: CowSwap has 3-5 dominant solvers. If they
    // collude—even implicitly through algorithmic pricing—users
    // lose the benefit of the "competition" model entirely.
    //
    // Pattern #80: Solver Cartel via Implicit Collusion

    // Detection: Monitor solver profit margins vs reference price.
    // If margins are consistently higher than competitive baseline,
    // collusion may be occurring.
    //
    // Defense: Permissionless solver entry. Lower barriers → more
    // solvers → harder to collude. CowSwap's open solver registry
    // partially addresses this.
}

// ============================================================
// Attack #2: Solver Front-Running (Private Order Flow)
// ============================================================
contract Attack2_SolverFrontrunning {
    // VULNERABLE: Solver receives user intent BEFORE execution
    // Attack: Solver sees "buy 10 ETH worth of TOKEN" →
    // buys TOKEN for themselves first → executes user order
    // at higher price → profits from the spread
    //
    // This is the MEV problem (Pattern #34) applied to intent
    // architecture. The solver is both the executor AND the
    // potential front-runner.
    //
    // Pattern #81: Solver Front-Running via Order Flow Advantage

    // Defense: Dutch auction pricing on the intent side.
    // User specifies declining price over time → solver
    // can't front-run without risking the order going to
    // another solver at a lower price.
    //
    // UniswapX uses this: the order starts at a high price
    // and decays, so the first solver to fill gets the profit.
}

// ============================================================
// Attack #3: Reference Price Manipulation
// ============================================================
contract Attack3_ReferencePriceManipulation {
    // VULNERABLE: Solver price is measured against a "reference price"
    // Attack: Solver manipulates the reference price source
    // (e.g., Uniswap TWAP, Chainlink) → reference price drops
    // → solver's price appears better → solver wins more auctions
    //
    // If the solver is ALSO a validator (MEV-Boost), they can
    // manipulate the reference price and win the solver auction
    // in the same block. This is cross-domain manipulation.
    //
    // Pattern #82: Solver Oracle Manipulation via Validator Access
    //
    // Defense: Multi-source reference price with TWAP averaging
    // across multiple DEXs + CEX feeds.
}

// ============================================================
// Attack #4: Solver Credit Risk
// ============================================================
contract Attack4_SolverCreditRisk {
    // VULNERABLE: Solvers provide instant execution via credit
    // Attack: Solver executes 100 user orders → collects fees
    // → fails to settle with the protocol → protocol loses funds
    //
    // Unlike smart contracts (where code enforces settlement),
    // intent-based systems rely on solver honesty for settlement.
    // A solver that defaults on obligations creates a systemic loss.
    //
    // Pattern #83: Solver Default via Settlement Failure
    //
    // Defense: Solver must stake collateral (bond) that exceeds
    // maximum potential obligation. If solver defaults, bond is
    // slashed to compensate users.
    
    mapping(address => uint256) public solverBond;
    mapping(address => uint256) public solverOutstanding;
    
    function acceptOrder(address solver, uint256 value) external {
        require(
            solverBond[solver] >= solverOutstanding[solver] + value,
            "Insufficient bond"
        );
        solverOutstanding[solver] += value;
    }
}

// ============================================================
// Attack #5: Intent Replay (Cross-Chain)
// ============================================================
contract Attack5_IntentReplay {
    // VULNERABLE: Same signed intent can be executed on multiple chains
    // Attack: User signs "sell 1 ETH for USDC on Ethereum" →
    // solver also executes it on Polygon (where it's also valid)
    // → user loses funds on Polygon
    //
    // This is Pattern #17 (Cross-Chain Replay) applied to intents.
    // The intent signature doesn't include chainId → replayable.
    //
    // Pattern #84: Cross-Chain Intent Replay
    //
    // Fix: Include chainId in the EIP-712 domain separator
    // and in the signed intent data.
}

// ============================================================
// Attack #6: Intent Ambiguity via Partial Fill
// ============================================================
contract Attack6_IntentAmbiguity {
    // VULNERABLE: Solver can partially fill an intent
    // Attack: User signs "sell 10 ETH for USDC" →
    // solver fills 9.9 ETH → keeps 0.1 ETH as "gas fee"
    // → user receives less than expected
    //
    // The user's intent was "sell ALL 10 ETH" but the solver
    // interpreted it as "sell up to 10 ETH." Ambiguity in
    // intent specification creates profit for the solver.
    //
    // Pattern #85: Intent Ambiguity Exploitation
    //
    // Fix: User specifies exact fill requirements:
    // "ALL or nothing" vs "partial OK" as an explicit parameter.
    
    enum FillType { ALL_OR_NOTHING, PARTIAL_OK }
    
    struct Intent {
        address tokenIn;
        address tokenOut;
        uint256 amountIn;
        uint256 minAmountOut;
        FillType fillType;  // Explicit fill requirement
        uint256 deadline;
        uint256 chainId;    // Anti-replay
        uint256 nonce;      // Anti-replay
    }
}

// ============================================================
// Summary: 6 Patterns Added (#80-85)
// ============================================================
// Intent architecture inverts the traditional DeFi security model.
// Instead of "code decides execution," it's "solver decides execution."
// Every solver is a semi-trusted intermediary, and the security
// of the entire system depends on solver incentives remaining
// aligned with user interests.
//
// The question intent protocols must answer:
// "What stops a profit-maximizing solver from extracting all
// available value from user orders?"
// 
// Current answer: Competition. But competition requires:
// 1. Low barriers to entry (many solvers)
// 2. Transparent pricing (reference price integrity)
// 3. Enforceable settlement (solvers can't default)
// 4. Non-collusive incentives (solvers can't coordinate)
//
// All four are assumptions, not guarantees.
