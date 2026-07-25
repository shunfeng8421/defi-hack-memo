# Solang Security Analysis — Solidity → Solana Compiler

**Project**: hyperledger-solang/solang (⭐1,383, Rust, Apache-2.0)  
**Function**: Compiles Solidity to Solana BPF / Polkadot WASM / Stellar  
**Risk Class**: Compiler-Induced Vulnerabilities (CIV)

---

## The Compiler Trust Model

```
Solidity Source → [Solang] → BPF Bytecode → Solana Runtime
     ↑                                              ↓
  Auditor reads this                    But this is what actually executes
```

**Key Risk**: An auditor verifies the Solidity source. The runtime executes the BPF output. If Solang's translation is incorrect, the audit is worthless — the auditor never saw the executed code.

## Attack Surface

### 1. Integer Size Mismatch

| Solidity | Solana BPF |
|------|------|
| 256-bit integers | 64-bit registers |
| Automatic overflow check (0.8+) | Manual overflow handling |
| `uint256` native | Must emulate 256-bit math |

**Risk**: Solang's 256-bit emulation must correctly implement overflow checking. A bug in the emulation creates contracts that appear safe in Solidity but overflow in BPF.

### 2. Storage Layout Mapping

Solidity uses a key-value storage model. Solana uses accounts with serialized data. Solang must correctly map:

```
Solidity mapping(address => uint256)  →  Solana PDA derivation + account data
```

**Risk**: Incorrect account derivation creates storage collision — two different Solidity storage slots mapping to the same Solana account.

### 3. Cross-Contract Call Semantics

Solidity's `CALL` opcode differs fundamentally from Solana's CPI (Cross-Program Invocation):

| Solidity CALL | Solana CPI |
|------|------|
| Call any address | Call must specify program ID + accounts |
| Returns success/failure | Returns program result |
| Reentrancy possible | Reentrancy prevented by design |

**Risk**: Solang must correctly implement Solidity's call semantics on Solana's CPI model. If Solang wraps a failing CPI as a "success" return, contracts may incorrectly believe external calls succeeded.

### 4. ABI Encoding Differences

Solidity uses ABI-encoded calldata. Solana uses Borsh or custom serialization. Solang must translate between the two:

```
Solidity: keccak256(signature)[0:4] + abi.encode(args)
Solana:  instruction_data (custom format)
```

**Risk**: If Solang's ABI decoder has a bug (e.g., accepting extra bytes in calldata), contracts compiled via Solang may accept malformed input that native Solidity would reject.

## Verification Methodology

Solang has:
- ✅ 1,383 stars — actively maintained
- ✅ Hyperledger project — governance oversight
- ✅ Test suite (solana_tests, polkadot_tests, evm_tests)
- ⚠️ Compiler verification is inherently harder than contract verification

**Recommendation**: Any protocol deploying to Solana via Solang should:
1. Deploy the SAME contract via native Solidity (Ethereum) AND Solang (Solana)
2. Run identical test suites on both deployments
3. Fuzz the ABI boundary for encoding mismatches
4. Verify storage layout mapping for all state variables

## Our 66-Pattern Relevance

Compiler-induced vulnerabilities span multiple patterns:
- Pattern #17 (Cross-Chain Replay) if chainId is mishandled
- Pattern #29 (Arithmetic) if overflow emulation is wrong
- Pattern #51-58 (Solana patterns) if account derivation is incorrect

However, *compiler bugs are upstream of all 66 patterns* — they can introduce any vulnerability type in the compiled output.

## Conclusion

Solang is a critical infrastructure project. A bug in Solang affects every contract compiled through it. The project's active maintenance and test coverage are positive signs, but the fundamental challenge of cross-language compilation means that **contracts deployed via Solang have an additional trust assumption**: they trust the compiler.

This is not unique to Solang — the Solidity compiler (solc) has the same trust model. The difference is that solc has 10+ years of battle testing, while Solang is newer and targets a more complex compilation target (multi-chain).
