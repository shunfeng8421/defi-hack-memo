# Chapter 23: Writing Effective Tests

*"A test that proves your code works is a unit test. A test that proves someone else's code breaks is a security audit."*

---

## The 105-Pattern Foundry Test Suite

Every pattern in this book has a corresponding Foundry test. The test proves that the vulnerability exists—not by describing it, but by executing it. Running `forge test` reproduces the attack against real on-chain state, demonstrating the exploit in a way that no static description can match.

```solidity
function test_Attack1_SpotPriceManipulation() public {
    // Setup: victim deposits — the state before the attack
    vm.startPrank(victim);
    vault.deposit(10 ether);
    uint256 sharesBefore = vault.shares(victim);
    
    // Attack: manipulate spot price via flash-loaned swap
    vm.startPrank(attacker);
    uint256 flashLoanAmount = 100 ether;
    vault.swap(flashLoanAmount, 0); // Dump reserves → price collapses
    
    // Exploit: attacker deposits at manipulated price → inflated shares
    vault.deposit(1 ether);
    uint256 attackerShares = vault.shares(attacker);
    
    // Verify: attacker got >1.5x the shares they deserved
    assertGt(attackerShares, 1.5 ether);
    
    // Verify: victim's shares are now worth less than their deposit
    uint256 victimValue = vault.getValueOfShares(sharesBefore);
    assertLt(victimValue, 10 ether); // Victim lost value
}
```

This test doesn't describe a flash loan attack. It performs one. Any auditor, developer, or researcher can clone the repository and verify every claim in this book by running one command: `forge test`.

---

## The Security Test Pyramid

Traditional software testing uses a pyramid: many unit tests at the base, fewer integration tests, fewest end-to-end tests. Security testing inverts this pyramid:

| Layer | Traditional Priority | Security Priority | Rationale |
|------|:--:|:--:|------|
| Unit tests | 🔺 Most | 🔻 Some | Individual functions are rarely the attack surface |
| Fuzzing | 🔺 Some | 🔺 More | Random inputs find edge cases humans miss |
| Invariant tests | 🔻 Rare | 🔺 Most | Protocol-level properties catch interaction bugs |
| Fork tests | ❌ Not used | 🔺 Essential | Real mainnet state reveals cross-protocol attacks |
| Integration tests | 🔻 Few | 🔺 Essential | Attackers exploit multi-protocol interactions |

The inversion is rational. Attackers do not unit-test your code. They compose transactions across your protocol, the DEX your oracle reads from, the lending market your tokens trade on, and the bridge your messages cross. Unit tests test one function. Attackers test the entire ecosystem.

---

## Writing an Attack Simulation

Every security test follows the same four-step structure:

### Step 1: Set Up the Vulnerable State

Deploy the contracts, fund the accounts, set the oracle prices. This is the "before" picture—the state that existed before the attack.

```solidity
function setUp() public {
    // Deploy protocol
    vault = new VulnerableVault(token);
    
    // Fund victim
    deal(address(token), victim, 100 ether);
    vm.prank(victim);
    token.approve(address(vault), 100 ether);
    vm.prank(victim);
    vault.deposit(10 ether); // Victim has legitimate deposit
    
    // Fund attacker (minimal — flash loan will provide the rest)
    deal(address(token), attacker, 1 ether);
}
```

### Step 2: Execute the Attack

Perform the exact sequence of transactions the attacker would use. This is the "during" picture.

```solidity
function test_Exploit() public {
    vm.startPrank(attacker);
    
    // 1. Take flash loan
    flashLender.flashLoan(address(this), address(token), 100 ether, "");
    
    // 2. Manipulate oracle
    router.swapExactTokensForTokens(100 ether, 0, path, address(this), deadline);
    
    // 3. Exploit inflated price
    vault.deposit(1 ether); // Gets inflated shares
    
    // 4. Withdraw at inflated valuation
    vault.withdraw(vault.balanceOf(attacker));
    
    // 5. Repay flash loan
    token.transfer(address(flashLender), 100 ether + fee);
}
```

### Step 3: Verify the Damage

Assert that the attacker's balance increased, the protocol's balance decreased, or an invariant was broken. This is the "after" picture.

```solidity
    // Attacker profited
    uint256 attackerBalance = token.balanceOf(attacker);
    assertGt(attackerBalance, 1 ether); // Made more than initial capital
    
    // Protocol lost funds
    uint256 vaultBalance = token.balanceOf(address(vault));
    assertLt(vaultBalance, 10 ether); // Less than victim's deposit
}
```

### Step 4: Apply the Fix and Re-Verify

Change the vulnerable code and re-run the test. The test should now fail—the attack is no longer possible.

A test that passes when the vulnerability exists and fails after the fix is applied is a valid security test. A test that passes both before and after the fix proves nothing.

---

## Fork Testing: The Gold Standard

Foundry can fork any Ethereum block, giving your test access to real state:

```solidity
function test_PancakeBunnyAttack() public {
    // Fork BSC at the block BEFORE the exploit
    vm.createSelectFork("bsc", 7_500_000);
    
    // Now you have:
    // - Real PancakeBunny contracts with real state
    // - Real PancakeSwap pools with real liquidity
    // - Real BUNNY token with real holders
    // - Real attacker contract deployed on-chain
    
    // Execute the exploit against the frozen state
    // If it succeeds, the vulnerability is confirmed
    
    // The test proves:
    // 1. The attack would have succeeded on mainnet
    // 2. The exact amount the attacker could have stolen
    // 3. The specific inputs needed for the exploit
}
```

Fork testing is the gold standard for exploit verification. It proves the attack would have succeeded on mainnet at the time it occurred, not just in a simplified test environment. Every test in our 105-test suite runs against a fork of the chain where the attack occurred.

**When to Use Fork Tests**:
- Verifying historical exploits (did this attack really work?)
- Testing protocol interactions (does my protocol break when interacting with real Uniswap?)
- Validating oracle assumptions (does Chainlink's update frequency match my protocol's needs?)

**When NOT to Use Fork Tests**:
- Testing new contracts that haven't been deployed yet
- Testing against chains without public RPC nodes
- Running in CI with tight time limits (fork tests take 5-30 seconds each)

---

## Invariant Testing: Prove What Must Always Be True

An invariant is a property that must hold after ANY sequence of valid operations. Chapter 13 (Solana) and Chapter 22 (Scanner) introduced invariants. Here is how to test them:

```solidity
contract VaultInvariants is Test {
    Vault vault;
    Handler handler;
    
    function setUp() public {
        vault = new Vault();
        handler = new Handler(vault);
        
        // Set target contract and handler functions
        targetContract(address(handler));
    }
    
    // Foundry will randomly call handler functions in random order,
    // then check this invariant after each call
    function invariant_SupplyConservation() public {
        uint256 totalDeposits = vault.totalDeposits();
        uint256 totalShares = vault.totalShares();
        uint256 contractBalance = token.balanceOf(address(vault));
        
        // If totalShares > 0, contract must hold at least totalDeposits worth
        assertGe(contractBalance, totalDeposits);
    }
}

contract Handler {
    Vault vault;
    
    function deposit(uint256 amount) external {
        amount = bound(amount, 1, 100 ether);
        vault.deposit(amount);
    }
    
    function withdraw(uint256 shares) external {
        shares = bound(shares, 0, vault.balanceOf(address(this)));
        vault.withdraw(shares);
    }
}
```

Foundry's fuzzer will try thousands of random sequences of `deposit()` and `withdraw()` calls, attempting to break `invariant_SupplyConservation`. If it finds a sequence that breaks the invariant, it reports the exact sequence that caused the failure. This is vastly more powerful than writing individual tests because it tests ALL sequences, not just the ones you thought to write.

---

## The Test Quality Checklist

1. **The test FAILS after the fix is applied.** If the test passes after the fix, it's not testing the vulnerability—it's testing the happy path.
2. **The test uses MAINNET fork state when available.** Isolated test environments hide cross-protocol attack vectors.
3. **The test VERIFIES state damage, not just execution success.** `assertEq(vault.balance, 0)` is stronger than `assert(!reverted)`.
4. **The test has a CLEAR name.** `test_Attack1_SpotPriceManipulation` tells you what it tests. `test_exploit1` does not.
5. **The test is REPRODUCIBLE.** Anyone with Foundry installed should be able to clone, run `forge test`, and see the same results.

---

*Next: Chapter 24 — Incident Response Checklist*
