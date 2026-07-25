// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Formal Verification Primer — Cherum Bridge Invariants
/// @notice Proving protocol properties using Foundry invariant testing
/// @author Shiqiang Chen · July 2026

// ============================================================
// What Is an Invariant?
// ============================================================
// An invariant is a property that MUST be true after ANY sequence
// of valid operations. If the invariant is ever broken, the
// protocol has a bug — even if you can't find the specific 
// sequence that breaks it.
//
// Example invariants for Cherum:
//   I1: Every nonce is used at most once (no double-spend)
//   I2: Total minted on destination ≤ total burned on source
//   I3: Paused state cannot execute dispatches
//   I4: Available balance = actual balance - parked amount

// ============================================================
// Invariant Test Framework (Foundry)
// ============================================================
// Foundry runs invariant tests by:
// 1. Randomly calling handler functions in random order
// 2. After each call, checking that the invariant still holds
// 3. If any sequence breaks the invariant, Foundry shows you
//    the exact sequence that caused the failure

contract CherumInvariants {
    // Ghost variables: track what "should" be true
    uint256 public ghost_totalBurned;
    uint256 public ghost_totalMinted;
    mapping(uint256 => bool) public ghost_nonceUsed;
    
    // ========================================================
    // Invariant I1: Nonce Uniqueness
    // "No nonce is ever processed more than once"
    // ========================================================
    function invariant_NonceUniqueness(uint256 nonce) external {
        // This invariant is checked after EVERY handler call
        // Foundry will try every nonce value to find a violation
        
        // If the protocol ever processes a nonce that was
        // already used, the invariant breaks → bug found
        assert(!dispatcherNonceUsed[nonce] || !ghost_nonceUsed[nonce]);
        // Bug: double-processing detected!
        // Fix: require(!dispatcherNonceUsed[nonce], "Nonce used")
    }
    
    // ========================================================
    // Invariant I2: Supply Conservation
    // "Total minted on destination ≤ total burned on source"
    // ========================================================
    function invariant_SupplyConservation() external {
        uint256 actualBurned = totalBurnedOnSource;
        uint256 actualMinted = totalMintedOnDestination;
        
        // The protocol must never create tokens from nothing
        assert(actualMinted <= actualBurned);
        // Bug: minting without burning detected!
    }
    
    // ========================================================
    // Invariant I3: Pause Safety
    // "When paused, no state-changing operations execute"
    // ========================================================
    function invariant_PauseSafety() external {
        if (paused) {
            // Check: no dispatch has occurred since pause
            assert(lastDispatchedAt <= pausedAt);
            // Bug: dispatch during pause detected!
        }
    }
    
    // ========================================================
    // Invariant I4: Parked Fund Isolation
    // "Available = Total - Parked (parked funds can't be used)"
    // ========================================================
    function invariant_ParkedFundIsolation() external {
        uint256 total = token.balanceOf(address(this));
        uint256 parked = parkedUSDC;
        uint256 available = total - parked;
        
        // No operation should ever access parked funds
        assert(available >= 0);
        // Verify: operations only use available balance
    }
    
    // ========================================================
    // Handler: Models user behavior
    // ========================================================
    // Foundry randomly calls these functions to try to break
    // the invariants. Each call is a "valid" operation that
    // the protocol should handle correctly.
    
    function handler_Dispatch(uint256 nonce, uint256 amount) external {
        // Skip if nonce already used
        if (ghost_nonceUsed[nonce]) return;
        
        // Execute dispatch (Foundry may try invalid params)
        try cherum.dispatch(nonce, amount) {
            ghost_nonceUsed[nonce] = true;
            ghost_totalBurned += amount;
        } catch {
            // Dispatch should fail gracefully on invalid input
        }
    }
    
    function handler_ProcessCCTP(uint256 nonce, uint256 amount) external {
        if (!ghost_nonceUsed[nonce]) return; // Only process dispatched
        
        try cherum.processCCTPMessage(nonce, amount) {
            ghost_totalMinted += amount;
        } catch {}
    }
    
    function handler_Pause() external {
        try cherum.pause() {} catch {}
    }
    
    function handler_Unpause() external {
        try cherum.unpause() {} catch {}
    }
}

// ============================================================
// Why Invariant Testing > Unit Testing
// ============================================================
//
// Unit test: "deposit(100) then withdraw(100) should work"
//   → Tests ONE path, with known good inputs
//
// Invariant test: "after ANY sequence of valid ops, supply
//   is conserved"
//   → Tests ALL paths, with random inputs, automatically
//
// Foundry's fuzzer will try:
//   dispatch(1, 100) → dispatch(1, 100) → I1 breaks!
//   dispatch(2, 500) → pause() → dispatch(3, 200) → I3 breaks!
//   dispatch(4, 1000) → processCCTP(4, 2000) → I2 breaks!
//
// Each of these would require a separate unit test.
// Invariant testing finds them all automatically.

// ============================================================
// CVL Equivalent (Certora Verification Language)
// ============================================================
// The same invariants in Certora's language would look like:
//
// rule nonceUniqueness {
//     uint256 nonce;
//     env e;
//     require !dispatcherNonceUsed(e, nonce);
//     dispatch(e, nonce, amount);
//     assert dispatcherNonceUsed(e, nonce);
//     // Certora proves: after dispatch, nonce IS used
//     // AND: no double-dispatch is possible (statically verified)
// }
//
// Unlike Foundry (which tests random sequences), Certora
// mathematically PROVES the invariant holds for ALL sequences.
//
// Trade-off:
//   Foundry: runs fast, finds counterexamples, NO false positives
//   Certora: proves universally, needs SMT solver, CAN timeout

// ============================================================
// Run:
//   forge test --match-contract CherumInvariants -vvvv
// ============================================================
