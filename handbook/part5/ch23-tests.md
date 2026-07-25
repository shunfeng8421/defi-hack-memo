# Chapter 23: Writing Effective Tests

*"A test that proves your code works is a unit test. A test that proves someone else's code breaks is a security audit."*

---

## The 105-Pattern Foundry Test Suite

Every pattern in this book has a corresponding Foundry test. The test proves that the vulnerability exists—not by describing it, but by executing it.

```solidity
function test_Attack1_SpotPriceManipulation() public {
    // Setup: victim deposits
    vm.startPrank(victim);
    vault.deposit(10 ether);
    uint256 sharesBefore = vault.shares(victim);
    
    // Attack: manipulate spot price
    vm.startPrank(attacker);
    vault.swap(100 ether, 0); // Dump reserves → price drops
    
    // Verify: attacker gets inflated shares
    vault.deposit(1 ether);
    uint256 attackerShares = vault.shares(attacker);
    assertGt(attackerShares, 1.5 ether); // Got >1.5x what they should
}
```

This test doesn't describe a flash loan attack. It performs one. Running `forge test` executes the attack and verifies the result. Any auditor, developer, or researcher can clone the repository and verify every claim in this book by running one command.

---

## The Test Pyramid for Security

| Layer | What It Tests | Tool |
|------|------|------|
| Unit | Single function correctness | `forge test` |
| Fuzzing | Random inputs find edge cases | `forge test` with fuzz |
| Invariant | Protocol properties always hold | `forge test` with invariant |
| Fork | Attack on mainnet state | `forge test` with fork |
| Integration | Multi-protocol interaction | End-to-end scripts |

The security testing pyramid is inverted from the traditional testing pyramid. Most projects have many unit tests and few integration tests. Security testing needs the opposite: many fork tests against real mainnet state, because vulnerabilities emerge from protocol interactions that unit tests never exercise.

---

## Writing an Attack Simulation

1. **Set up the vulnerable state**: Deploy the contracts, fund the accounts, set the oracle prices
2. **Execute the attack**: Perform the exact sequence of transactions the attacker would use
3. **Verify the damage**: Assert that the attacker's balance increased, the protocol's balance decreased, or the invariant was broken
4. **Apply the fix**: Change the vulnerable code, re-run the test, verify the attack now fails

A test that passes when the vulnerability exists and fails after the fix is applied is a valid security test. A test that passes both before and after the fix proves nothing.

---

## Fork Testing

Foundry can fork any Ethereum block, giving your test access to real state:

```solidity
function test_PancakeBunnyAttack() public {
    vm.createSelectFork("bsc", 7_500_000); // BSC block before the exploit
    
    // Now you have:
    // - Real PancakeBunny contracts with real state
    // - Real PancakeSwap pools with real liquidity
    // - Real BUNNY token with real holders
    
    // Execute the exploit against the frozen state
    // If it succeeds, the vulnerability is confirmed
}
```

Fork testing is the gold standard for exploit verification. It proves the attack would have succeeded on mainnet at the time it occurred, not just in a simplified test environment.

---

*Next: Chapter 24 — Incident Response*
