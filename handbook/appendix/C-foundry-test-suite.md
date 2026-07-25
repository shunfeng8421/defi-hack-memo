# Appendix C: Foundry Test Suite Quick Start

```bash
# 1. Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# 2. Clone the repo
git clone https://github.com/shunfeng8421/defi-hack-memo.git
cd defi-hack-memo

# 3. Run all 105 tests
forge test -vvv

# 4. Run specific pattern
forge test --match-test test_Attack1_SpotPrice

# 5. Fork a mainnet block to verify real attacks
forge test --fork-url https://eth.llamarpc.com --fork-block-number 19000000
```

## Test Structure

Each test proves one attack pattern:
- Sets up the vulnerable contract
- Executes the exact attack sequence
- Asserts the exploit succeeded
- Shows the fix (making the test pass after patching)

Tests in: `pocs/test-suite/AttackTestSuite.t.sol`
