# Chapter 18: ZK Circuit Vulnerabilities

*"A zero-knowledge proof proves that a computation was performed correctly. It does not prove that the correct computation was performed."*

---

## The Tornado Cash Lesson

Tornado Cash was the most widely used privacy protocol in DeFi. Users deposited ETH into a pool, received a cryptographic note proving their deposit, and could later withdraw to a fresh address by proving they held a valid note—without revealing which deposit their withdrawal corresponded to. The privacy guarantee depended on a ZK circuit that verified the note without revealing its contents.

In February 2023, a security researcher discovered that Tornado Cash's circuit had a subtle flaw in its nullifier derivation. The nullifier—a value derived from the deposit note that prevented double-spending—was not properly constrained. A user could withdraw the same deposit multiple times by providing different values for the unconstrained portion of the circuit, each value producing a different (valid) nullifier.

The bug was never exploited on mainnet because the Tornado Cash UI did not allow users to construct the malicious input. But the circuit was verifiably broken: a valid proof could be generated for an invalid withdrawal. The only thing preventing exploitation was the lack of a user interface to construct the attack.

This is the nightmare scenario of ZK security: **the proof verifies successfully. The circuit is wrong. No one notices until someone builds the right interface.**

---

## Why ZK Circuits Are Uniquely Dangerous

Traditional smart contracts have a clear execution model. You can trace every state change, simulate every transaction, and test every code path. If a function has a bug, the bug manifests in a failed transaction or incorrect state.

ZK circuits have no execution trace visible at verification time. The verifier receives a proof and accepts or rejects it. If the proof is accepted, the verifier has no way to know whether the underlying computation was correct—only that the proof checked out. A bug in the circuit does not cause a failed proof. It causes a valid proof of a false statement.

This is the fundamental asymmetry of ZK security: **a bug in traditional code produces incorrect output. A bug in a ZK circuit produces a valid proof of incorrect output.** The bug is invisible to the verifier.

---

## Pattern #54: Unconstrained Signal (Under-Constrained Circuit)

**Severity**: CRITICAL
**Real cases**: Tornado Cash nullifier bug, multiple ZK-rollup circuit fixes

### The Vulnerability

Circom—the dominant ZK circuit language—has two assignment operators. The difference between them is the single most important concept in ZK security:

```circom
// <== : Constrained assignment. The value is mathematically constrained.
// The prover MUST satisfy the equation for the proof to be valid.
signal output c;
c <== a + b;  // Prover must provide c such that c = a + b

// <-- : Unconstrained assignment. The prover can set ANY value.
// This is for intermediate computation only. NEVER for proof-critical signals.
signal temp;
temp <-- computeHash(secret);  // Prover can set temp to ANYTHING!
```

Using `<--` on a signal that affects the proof output allows the prover to forge the proof:

```circom
// ❌ VULNERABLE: hash assigned with <-- (unconstrained)
signal input secret;
signal output publicHash;
publicHash <-- poseidon([secret]);  // Prover can set publicHash to anything!
// The proof is valid. The publicHash is fake.

// ✅ SAFE: hash assigned with <== (constrained)
publicHash <== poseidon([secret]);  // Prover MUST use the actual hash
```

### Detection

Tools like `circomspect` scan for `<--` usages on output signals. Manual review must verify every `<--` in the circuit and confirm it is used only for intermediate computation that does not affect the proof's correctness.

---

## Pattern #55: Overflow Wrapping in Prime Fields

**Severity**: HIGH

### The Vulnerability

Circom operates on a prime field `p = 21888242871839275222246405745257275088548364400416034343698204186575808495617`. This is a 254-bit prime. Solidity operates on 256-bit integers. The difference of 2 bits creates a type-mismatch attack surface.

```circom
// Circom: arithmetic modulo p (~2^254)
signal a;
a <== 2**253;  // Fine in Circom

// Solidity: arithmetic modulo 2^256
uint256 a = 2**253;  // Fine in Solidity
uint256 b = 2**254;  // Also fine in Solidity, but wraps in Circom!
```

A value that is valid in Solidity (2^254) wraps around p in Circom, becoming a much smaller value. An attacker can:
1. Submit a proof with input value = 2^254
2. The Circom circuit wraps this to a small value → passes all range checks
3. The Solidity verifier sees 2^254 → accepts a massive value that should have been rejected

### The Fix

Range-check all inputs in the circuit:

```circom
component rangeCheck = Num2Bits(253);
rangeCheck.in <== input;  // Ensures input < 2^253
// Circuit rejects any input >= 2^253, preventing wrap attacks
```

---

## Pattern #56: Trusted Setup Compromise

**Severity**: CRITICAL

### The Vulnerability

Groth16—the most widely used proving system—requires a one-time trusted setup ceremony. During the ceremony, participants generate random values that form the proving and verification keys. If all participants collude or if the "toxic waste" (the random values) leaks, anyone who possesses the toxic waste can generate valid proofs for any statement.

A compromised setup means:
- Prove "I have 1 ETH" when you have 0 ETH
- Prove "I deposited into Tornado Cash" when you never deposited
- Prove "this rollup transaction is valid" when it transfers all funds to the attacker

### The Fix

- **Multi-Party Ceremony**: The setup is secure if at least ONE participant is honest and destroys their random values. Ethereum's KZG ceremony had over 140,000 participants.
- **Universal Setup**: PLONK/KZG use a single setup for all circuits. The ceremony only needs to happen once.
- **Transparent Setup**: STARKs require no trusted setup at all.

---

## Pattern #57: Recursive Proof Amplification

**Severity**: HIGH

### The Vulnerability

A recursive proof system verifies proofs within proofs: proof A verifies proof B which verifies proof C, forming a chain. If any proof in the chain has a subtle bug—a single unconstrained signal, a single missing range check—the bug propagates through the entire recursion.

A ZK-rollup that verifies thousands of transactions by recursively proving batches is vulnerable to this amplification. One bug in one batch proof = all subsequent proofs are compromised.

### The Fix

Formal verification of the recursive circuit logic. The entire recursion chain must be proven correct, not just individual steps.

---

## The ZK Circuit Checklist

1. **Every `<--` is on a signal that does not affect the proof output.** Audit with `circomspect`.
2. **Every input is range-checked.** Solidity's 256-bit inputs must be constrained to < 2^253.
3. **Trusted setup is multi-party and verifiable.** At least one honest participant must be confirmed.
4. **Recursive circuits are formally verified.** One bug in one step = all steps are compromised.

---

## Connection to Other Chapters

- **Ch17 (DePIN)**: Filecoin's storage proofs depend on SNARK circuits. A missing constraint enables proof forgery without storage—a ZK circuit vulnerability enabling a DePIN attack.
- **Ch10 (Initialization)**: A trusted setup ceremony is an initialization procedure. The Uranium $50M lesson applies: initialization that anyone can compromise destroys the entire system.
- **Ch8 (Cross-Chain)**: ZK bridges use circuits to verify cross-chain state. A bug in the circuit means the bridge accepts invalid cross-chain messages—the same failure mode as Nomad's logic inversion.

---

*Next: Chapter 19 — RWA Tokenization Risks*
