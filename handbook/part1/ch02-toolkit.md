# Chapter 2: The Security Researcher's Toolkit

*"You don't need expensive tools. You need a workflow."*

---

## The Zero-Cost Stack

Every finding in this book — all 100 vulnerabilities, all 105 attack patterns, all 58 detection rules — was produced with tools that are completely free.

| Tool | Purpose | Lines of Code |
|------|------|:--:|
| Foundry | Smart contract testing | 752 (test suite) |
| Python 3.12 | Scanner scripting | 2,847 (defi-scanner.py) |
| Git + GitHub | Version control + publishing | — |
| VS Code | Code editor | — |
| curl + bash | API requests, automation | — |

This stack costs $0. No cloud services. No API subscriptions. No paid audit platforms. Everything runs locally.

The deliberate choice to use only free tools was not about saving money. It was about removing barriers. If the tooling required a $500/month subscription, only well-funded audit firms could use it. The hardening gradient would widen. By building everything on free infrastructure, any independent researcher — anywhere in the world — can replicate every result in this book.

---

## Foundry: Why It Matters

There are two major smart contract testing frameworks: Hardhat (JavaScript) and Foundry (Solidity). This book uses Foundry exclusively. The reason matters.

### The Translation Problem

Hardhat tests are written in JavaScript. Your attack simulation runs in a JavaScript VM. The actual protocol runs in the Ethereum Virtual Machine. These are not the same environment.

A Hardhat test can pass while the real attack fails — because JavaScript's number handling differs from Solidity's 256-bit integers, or because the JS VM's gas model is approximate, or because a subtle EVM opcode behavior is not replicated.

Foundry tests are Solidity code compiled to EVM bytecode. They run in the same execution environment as the protocol itself. When a Foundry test says "the attack succeeds," it means the attack would succeed on mainnet.

### The Fork Testing Advantage

Foundry can fork any Ethereum block. This means your test executes against the actual state of the blockchain at a specific moment in time.

```solidity
function test_AttackOnMainnetState() public {
    // Fork mainnet at block 19,000,000
    vm.createSelectFork("mainnet", 19_000_000);
    
    // Now you have:
    // - All real Uniswap pools with real liquidity
    // - All real Chainlink oracles with real prices
    // - All real token balances of real users
    
    // Your attack runs against the ACTUAL state
    // Not a mock. Not an approximation.
}
```

This is how we verified the PancakeBunny $120M attack. We forked the exact block before the exploit, executed the same transactions the attacker used, and watched the same result unfold. The test doesn't simulate the attack. It reproduces it.

### Installing Foundry

```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

That's it. One command. The entire toolchain — `forge` (testing), `cast` (RPC interaction), `anvil` (local node) — is installed.

### Running the 105-Pattern Test Suite

```bash
git clone https://github.com/shunfeng8421/defi-hack-memo.git
cd defi-hack-memo
forge test -vvv
```

Output:
```
Running 105 tests for pocs/test-suite/AttackTestSuite.t.sol:AttackTestSuite
[PASS] test_Attack1_SpotPriceManipulation()
[PASS] test_Attack2_CEIViolation()
[PASS] test_Attack3_FlashReentrancy()
...
[PASS] test_Attack105_CompleteTaxonomy()

Test result: ok. 105 passed; 0 failed; 0 skipped; finished in 12.34s
```

Every reader of this book can verify every claim by running one command. This is the difference between a security claim and a security proof.

---

## The 58-Pattern Scanner

The defi-scanner.py is 2,847 lines of Python. It uses regular expressions and keyword matching — not machine learning, not AI, not anything that requires a GPU or an API key.

### Why Pattern Matching?

Pattern matching has two advantages over ML-based approaches:

**1. Explainability.** When the scanner flags pattern #27 (EIP-712 Type Mismatch), it tells you exactly which line of code triggered the detection and why. An ML model says "this code is suspicious." The scanner says "this TYPEHASH is missing the `chainId` field that appears in the signed struct."

**2. No false negatives on novel patterns.** ML models detect what they were trained on. The scanner detects what you tell it to detect. When we discovered the EIP-712 struct-field mismatch pattern in giddyvaultv3, we added one regex rule. The scanner now catches it globally. An ML model would need retraining on new data.

### Scanner Architecture

```python
PATTERNS = {
    1: {
        "name": "Flash Loan + Spot Price Oracle",
        "severity": "CRITICAL",
        "regex": [r'getReserves\(\)', r'\.balance'],
        "keyword": ["price", "!TWAP", "!cumulative", "!Chainlink"],
        "description": "Instantaneous AMM price used in valuation",
        "fix": "Use TWAP oracle (Uniswap V2 consult()) or Chainlink"
    },
    # ... 57 more patterns
}
```

Each pattern has four components:
- **Regex**: One or more regular expressions that match vulnerable code patterns
- **Keyword**: Required keywords (must be present) and negated keywords (must be absent) for context
- **Description**: Human-readable explanation of why this pattern is dangerous
- **Fix**: Specific, actionable mitigation

The negated keyword check is what gives the scanner its discrimination power. Pattern #19 (Cross-Chain Replay) requires `keccak256` to be present AND `chainId` to be absent. A bridge that correctly includes chainId in its signature will not be flagged. A contract that signs messages without chainId will.

### Running the Scanner

```bash
python defi-scanner.py /path/to/contracts/
```

Output is a structured JSON report with severity levels, file locations, and fix recommendations. The same JSON format is consumed by the AI Auditor (Chapter 33) for automated report generation.

---

## The Exploitarium

The `exploits/` directory contains 20 verified proof-of-concept scripts for Web2 vulnerabilities:

| CVE | Product | Type |
|------|------|------|
| CVE-2026-20896 | Gitea | Authentication bypass |
| CVE-2025-29927 | NextJS | Middleware SSRF |
| CVE-2026-1470 | n8n | Sandbox escape |
| CVE-2025-57819 | FreePBX | SQL injection → RCE |

These are not collected from exploit databases. Each one has been independently verified — either by running against a known-vulnerable instance or by code review of the patched fix.

The exploitarium serves two purposes. First, it provides templates for responsible disclosure. When you find a vulnerability in a protocol, you know exactly what format to use. Second, it demonstrates a methodology. The Gitea bypass was found by asking: "What happens if I set the X-WEBAUTH-USER header?" The NextJS SSRF was found by asking: "What happens if I bypass the middleware?" This questioning methodology is more valuable than any single PoC.

---

## The Research Workflow

Every finding in this book followed the same six-step process:

### Step 1: Acquire
Get the source code. If it's a public repository, `git clone`. If it's a verified contract, use Sourcify or Etherscan's API. If it's a private audit, the protocol provides access.

### Step 2: Scan
Run the 58-pattern scanner. This takes 30 seconds and provides broad coverage. The goal is not to find vulnerabilities — it's to identify areas that require manual review.

### Step 3: Prioritize
Scanner output is noisy. 80% of matches are false positives. Human judgment filters the noise. Look for:
- CRITICAL severity patterns in core protocol logic (not test files, not libraries)
- Multiple patterns converging on the same file
- Patterns that match the protocol's specific risk profile (a bridge that flags cross-chain replay needs investigation; a DEX flagging the same pattern is noise)

### Step 4: Deep-Dive
Read every line of the flagged function. Trace the call path backward (who can call this?) and forward (what state does this affect?). This is where the scanner stops and human expertise begins.

### Step 5: Verify
Write a Foundry test that proves the vulnerability exists. Not a hypothetical — a test that would fail on mainnet. Submit the test with the vulnerability report.

### Step 6: Disclose
Follow the protocol's responsible disclosure policy. If they have a bug bounty program, use it. If they have a `security@` email, use that. If they have neither, contact the team directly. Never disclose publicly without giving the protocol reasonable time to fix.

---

## What This Chapter Did Not Cover

This chapter did not teach you Solidity. It did not explain how the EVM works. It assumed you already know these things. If you need to learn them, the Ethereum documentation and CryptoZombies are excellent resources. Come back when you can read and write smart contracts.

What this chapter gave you is a **workflow** — a reproducible, verifiable, free methodology for finding vulnerabilities in DeFi protocols. The rest of this book is about what to look for.

---

*Next: Chapter 3 — How to Read an Exploit Report*
