# Chapter 18: ZK Circuit Vulnerabilities

*"A zero-knowledge proof proves that a computation was performed correctly. It does not prove that the correct computation was performed."*

---

## The Circuit Trust Assumption

Zero-knowledge proofs are the most powerful cryptographic primitive in blockchain. They allow one party to prove to another that a statement is true without revealing any information beyond the validity of the statement itself. A ZK-rollup can compress thousands of transactions into a single proof. A privacy protocol can prove you have sufficient funds without revealing your balance.

But every ZK proof depends on a premise: **the circuit—the program that defines what is being proven—is correct.** If the circuit has a bug, the proof can be valid while the statement is false. The verifier says "this proof checks out." The circuit says "the prover has 100 ETH." The reality: the prover has 0 ETH and a buggy circuit accepted a forged input.

---

## Pattern #47: Unconstrained Signal (Under-constrained Circuit)

**Severity**: CRITICAL

### The Vulnerability

Circom—the dominant ZK circuit language—uses two assignment operators: `<==` (constrained) and `<--` (not constrained). Using `<--` on a signal that affects proof correctness allows the prover to set the signal to any value.

```circom
// ❌ VULNERABLE: <-- is not constrained
signal input secret;
signal output hash;
hash <-- poseidon([secret]);  // Prover can set hash to anything!
// Correct: hash <== poseidon([secret]);
```

### The Fix

Every signal that affects the proof output must use `<==`. Auditors must verify with `circomspect` or manual review that no `<--` appears on proof-critical signals.

---

## Pattern #48: Overflow Wrapping

**Severity**: HIGH

### The Vulnerability

Circom operates on a prime field `p = 21888242871839275222246405745257275088548364400416034343698204186575808495617`. Values larger than `p` wrap around:

```circom
signal a;
signal b;
a <== 2**253;
b <== 2**253;
c <== a + b;  // Wraps modulo p — not the real sum!
```

An attacker can submit inputs that appear small after wrapping but are actually massive.

### The Fix

Range-check all inputs:

```circom
component checkA = Num2Bits(253);
checkA.in <== a;  // Ensures a < 2^253
component checkB = Num2Bits(253);
checkB.in <== b;
```

---

## Pattern #49: Trusted Setup Leak

**Severity**: CRITICAL

### The Vulnerability

Groth16 requires a one-time trusted setup ceremony. The "toxic waste"—the random values generated during setup—can create valid proofs for any statement if leaked. The ceremony must have at least one honest participant to be secure.

### The Fix

Use transparent setups (STARKs) or universal setups (PLONK/KZG) that do not require per-circuit ceremonies.

---

*Next: Chapter 19 — RWA Tokenization*
