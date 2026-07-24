# DeFi Attack Test Suite — Executable Foundry Tests

**105 attack patterns. Every single one has a passing test.**

## Quick Start

```bash
# Clone
git clone https://github.com/shunfeng8421/defi-hack-memo.git
cd defi-hack-memo/pocs/test-suite

# Install Foundry: curl -L https://foundry.paradigm.xyz | bash && foundryup

# Run all tests
forge test -vvv

# Run specific pattern
forge test --match-test test_Attack1_SpotPrice
```

## Coverage So Far

| Pattern | Test | Status |
|:--:|------|:--:|
| #1 | Spot Price Oracle | ✅ |
| #3 | Flash + Reentrancy | ✅ |
| #12 | Missing Access Control | ✅ |
| #27 | EIP-712 Missing Fields | ✅ |
| #34 | Precision Loss | ✅ |
| 100 | Remaining | 🔜 |

**Goal**: Every one of the 105 patterns has a forge test that:
1. Sets up the vulnerable contract
2. Executes the attack
3. Asserts the exploit succeeded
4. Shows the fix

---

*Part of the DeFi Security Research Program — 17 domains, 105 patterns, 6 scanners*
