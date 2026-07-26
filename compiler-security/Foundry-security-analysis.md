# Foundry Security Analysis — 10K⭐ Development Framework

**Project**: foundry-rs/foundry (⭐10,516, Rust, Apache-2.0)  
**Function**: Ethereum development framework (compile, test, deploy, interact)  
**Risk Class**: Tooling-Induced False Confidence (TIFC)

---

## The Trust Model

```
Developer writes Solidity → Foundry compiles → Foundry EVM executes → Tests pass → Deploy to mainnet
                                    ↑                                                  ↓
                           Is this EVM identical?                          Is the real EVM identical?
```

**Key Risk**: If Foundry's EVM implementation differs from geth's EVM, tests that pass in Foundry do not guarantee the contract will behave correctly on mainnet. This is the same class of risk as Solang (Chapter 18): cross-implementation divergence.

---

## Architecture

| Crate | Purpose | Security Impact |
|------|------|------|
| `foundry-evm` | EVM implementation | ⚠️ CRITICAL — divergence from geth |
| `forge` | Test runner, script executor | ⚠️ HIGH — sandbox escape, script injection |
| `cast` | RPC interaction, transaction builder | ⚠️ HIGH — input sanitization, key exposure |
| `cheatcodes` | Test cheat system (vm.prank, vm.deal) | ⚠️ MEDIUM — false test results |
| `anvil` | Local dev node | ⚠️ MEDIUM — local exploits not in production |
| `fmt` | Code formatter | ✅ Low risk |

---

## Attack Surface 1: EVM Implementation Divergence

**Crate**: `foundry-evm`  
**Risk**: CRITICAL

The Revm (Rust EVM) crate that Foundry uses is NOT geth's EVM. It is a Rust reimplementation. While both follow the same yellow paper specification, implementation-level differences could cause:

| Scenario | Impact |
|------|------|
| `SELFDESTRUCT` behavior differs in edge cases | Deployed contract behaves differently than tested |
| Gas metering divergence | Contract runs out of gas on mainnet but not in Foundry |
| Precompile behavior differences (e.g., `MODEXP`) | Tests relying on precompile output pass incorrectly |
| EIP activation differences | Tests using EIP features not yet activated on mainnet behave differently |

**Verification**: Build a differential fuzzer that sends the same transaction to both Foundry's EVM and a real geth node, comparing state roots after each transaction. Any divergence is a vulnerability.

**Mitigation**: Foundry should document ALL known differences from geth EVM behavior. Currently, no such document exists.

---

## Attack Surface 2: Cheatcodes Producing Invalid Test Results

**Crate**: `cheatcodes`  
**Risk**: MEDIUM

Foundry's cheatcode system (`vm.prank()`, `vm.deal()`, `vm.warp()`) allows tests to manipulate blockchain state. If these cheatcodes do not perfectly replicate real blockchain behavior, tests may pass under conditions that would fail on mainnet:

```solidity
vm.prank(attacker);  // Impersonate attacker
vm.deal(attacker, 100 ether);  // Give attacker ETH they don't actually have
// Test passes because cheatcodes created impossible state
```

The cheatcodes are designed for testing convenience, but they can mask:
- Real gas costs (cheatcodes are gas-free)
- MEV extraction (no mempool competition in tests)
- Chain reorganization (test chain is single-block)
- Oracle staleness (test environment has perfect price data)

**Mitigation**: Every test that passes with cheatcodes should be complemented by a fork test that uses real mainnet state without cheatcodes.

---

## Attack Surface 3: Script Injection via Cast

**Crate**: `cast`  
**Risk**: HIGH

Cast constructs and sends transactions to RPC endpoints. If user-provided input is not properly sanitized before being passed to the RPC:

```bash
cast send 0xContract "function(string)" "$USER_INPUT"
```

A malicious `$USER_INPUT` could:
- Inject additional RPC parameters
- Redirect transactions to a different contract
- Modify gas parameters to create unexpected behavior

**Mitigation**: All user inputs to `cast` should be validated against expected types before being passed to transaction construction.

---

## Attack Surface 4: Arbitrary Code Execution via Script Deployments

**Crate**: `forge`  
**Risk**: HIGH

Forge scripts (`forge script`) execute arbitrary Solidity code in the Foundry EVM context. The script has access to:
- Private keys (via `--private-key`)
- RPC endpoints (via `--rpc-url`)
- File system access (via cheatcodes)

A malicious Foundry script—for example, one pulled from an untrusted GitHub repository—could:
- Exfiltrate private keys
- Send transactions to mainnet without user confirmation
- Deploy backdoor contracts

This is not a vulnerability in Foundry. It is a supply chain risk in Foundry's execution model. The risk is documented but not widely understood.

---

## Recommendation

1. **Differential Fuzzing**: Build an automated tool that runs identical transactions on Foundry's EVM and geth's EVM, flagging any state divergence. This is the single most valuable security improvement for the Foundry ecosystem.

2. **Cheatcode Audit**: Every Foundry cheatcode should have a corresponding fork test that validates the same behavior without cheatcodes.

3. **Cast Input Validation**: All CLI inputs to `cast` should be sanitized against a whitelist of expected types.

4. **Script Isolation**: `forge script` should run in a sandboxed environment that prevents file system access and requires explicit user confirmation for mainnet transactions.

---

## Foundry vs Our Tools

| Our Tool | Foundry Equivalent | Security Difference |
|------|------|------|
| 58-pattern scanner | forge test | Scanner finds bugs; forge proves fixes |
| 105 Foundry tests | forge test suite | Our tests prove exploits; Foundry framework runs them |
| GitHub Action | forge CI | Both automate the security pipeline |
| Certora spec (Ch22) | forge invariant | Certora proves invariants; forge finds counterexamples |

Foundry is our primary tool. Auditing Foundry is auditing our own infrastructure. Any bug in Foundry that causes us to miss a vulnerability is a bug in our security pipeline.

---

## Verdict

| Category | Score |
|------|:--:|
| EVM Correctness | 7/10 (no differential test suite) |
| Cheatcode Safety | 6/10 (can mask real failures) |
| Script Security | 5/10 (supply chain risk) |
| Cast Input Safety | 6/10 (no known validation layer) |
| **Overall** | **6/10** |

Foundry is the best Ethereum development framework. It is also a critical infrastructure dependency whose security model is under-documented and under-audited. Protocols that build on Foundry should understand these risks and implement compensating controls—specifically, fork-testing and differential EVM validation.
