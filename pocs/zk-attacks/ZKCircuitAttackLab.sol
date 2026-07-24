// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title ZK Circuit Attack Lab — 6 Zero-Knowledge Proof Vulnerabilities
/// @notice ZK = "trustless" — but the circuits can be wrong
/// @author Shiqiang Chen · July 2026

// ============================================================
// #1: Missing Constraint (Under-constrained Circuit)
// ============================================================
contract Attack1_MissingConstraint {
    // Circom circuit MUST constrain every signal. If not, prover can forge.
    // 
    // Circom BUG:
    // signal input a, b;
    // signal output c;
    // c <== a * b;     // Constrained ✓
    // d <-- a + b;     // NOT constrained ✗ — prover can set d to anything!
    //
    // Attack: Provide ANY value for d and proof still verifies
    // Real: Many early ZK protocols had unconstrained signals
    // Fix: Audit every signal for <== (not <--) constraint
}

// ============================================================
// #2: Soundness Bug — Overflow Wrapping
// ============================================================
contract Attack2_OverflowWrapping {
    // Circom operates on Prime field F_p where p = 21888242871839275222246405745257275088548364400416034343698204186575808495617
    // 
    // BUG: signal a = 2^253; signal b = 2^253;
    // signal c = a + b;  // Wraps around modulo p — not the "real" sum!
    //
    // Attack: Exploit modular arithmetic to bypass value range checks
    // Example: Prove you have balance > 1000 by wrapping a small balance
    //
    // Fix: Always add range checks: c < 2^252, a < 2^252, b < 2^252
}

// ============================================================
// #3: Signal Leakage via Public Inputs
// ============================================================
contract Attack3_SignalLeakage {
    // ZK proofs prove "I know x such that f(x, public) = true"
    // Public inputs MUST NOT leak private information
    //
    // BUG: circuit exposes hash(secret) as public input
    // Attack: Brute-force secret offline and match against public hash
    // Real: Tornado Cash nullifier hash was public (by design, but still a privacy leak)
    //
    // Fix: Use commitment schemes; never expose hashes of low-entropy secrets
}

// ============================================================
// #4: Trusted Setup Compromise
// ============================================================
contract Attack4_TrustedSetup {
    // Groth16 requires a trusted setup ceremony
    // If toxic waste (setup secrets) is obtained → unlimited fake proofs
    //
    // Attack: Compromise the MPC ceremony or use a malicious setup
    // Result: Create valid proofs for ANY statement
    //
    // Mitigations:
    // - Universal setup: PLONK/KZG (one-time, reusable)
    // - Transparent setup: STARK (no trusted setup at all)
    // - Multi-party ceremony: 1-of-N honest → safe
}

// ============================================================
// #5: Input Forgery via Non-Native Arithmetic
// ============================================================
contract Attack5_InputForgery {
    // Ethereum uses 256-bit integers; Circom uses 254-bit prime field
    // Type mismatch between EVM and ZK circuit verification
    //
    // BUG: Contract verifies proof with uint256 inputs
    // But circuit constrains values <= 2^254
    // Attacker can use values 2^254 to 2^256-1 that "wrap around" in circuit
    //
    // Example: Prover submits amount = 2^255 on-chain
    // Circuit sees amount mod p ≈ tiny value → passes range check
    // Contract uses actual 2^255 → massive over-withdrawal
    //
    // Fix: Range-check inputs in both circuit AND contract
}

// ============================================================
// #6: Recursive Proof Amplification
// ============================================================
contract Attack6_RecursiveAmplification {
    // Recursive proofs: proof A verifies proof B which verifies proof C...
    // If any step has a subtle bug, it propagates through the chain
    //
    // Attack: Find a single under-constrained gate in recursive circuit
    // Use it to inject fake computation that amplifies through recursion
    //
    // Real risk: zkRollup provers — if prover circuit has bug,
    // all rollup transactions can be forged
    //
    // Fix: Formal verification of recursive circuits; independent audits
}

/// @title ZK Summary
/// @dev ZK proves computation was done correctly — but only if the CIRCUIT is correct
/// The biggest risk: nobody reads the Circom code; they just trust the math
/// Your Aztec + VerusBridge ZK analysis is directly applicable here
