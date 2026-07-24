# Chapter 4: Flash Loan Attacks (Patterns 1-4)

Flash loans are the defining attack primitive of DeFi. They didn't exist before 2020. By 2024, they were involved in 40% of all DeFi exploits.

## Why Flash Loans Are Dangerous

A flash loan lets you borrow any amount with zero collateral — as long as you repay within the same transaction. This means:

- Attackers don't need capital
- The only cost is gas
- Any bug that requires "a lot of tokens" is now exploitable
- Traditional security assumptions ("nobody has that much money") break

## Pattern #1: Flash Loan + Spot Price Oracle

**Severity**: CRITICAL
**Real case**: PancakeBunny $120M (2021)

**The bug**: Protocol reads `getReserves()` from Uniswap V2 pool as the price. These reserves can be changed by swapping.

**The attack**:
1. Flash loan 100,000 ETH
2. Swap into the pool → reserves change → spot price drops 50%
3. Protocol reads fake price → values attacker's position at 2x real value
4. Attacker withdraws at inflated valuation
5. Repay flash loan → keep the difference

**The fix**: Use TWAP (time-weighted average price):
```solidity
// ❌ VULNERABLE
(uint256 r0, uint256 r1,) = pair.getReserves();
uint256 price = r0 * 1e18 / r1; // Spot — manipulable

// ✅ SAFE
uint256 price = pair.consult(token, amount); // Uniswap V2 TWAP
```

## Pattern #2: CEI Violation → Reentrancy

**Severity**: CRITICAL
**Real case**: DAO hack $60M (2016 — the original)

**The bug**: External call (transfer) happens BEFORE state update (balance decrease).

**The attack**:
1. Attacker deposits 10 ETH → balance[attacker] = 10
2. Attacker calls withdraw(10) → contract sends 10 ETH (external call)
3. Attacker's receive() callback → calls withdraw(10) AGAIN
4. balance[attacker] still = 10 (hasn't been updated yet)
5. Second withdraw succeeds → attacker gets 20 ETH total

**The fix**: Checks-Effects-Interactions pattern:
```solidity
// ✅ SAFE
function withdraw(uint256 amount) external {
    require(balance[msg.sender] >= amount);  // CHECK
    balance[msg.sender] -= amount;            // EFFECTS (first!)
    payable(msg.sender).transfer(amount);      // INTERACTIONS (last!)
}
```

## Pattern #3: Flash Loan + Reentrancy Combo

**Severity**: CRITICAL
**Real case**: CREAM Finance $130M (2021)

The deadliest combo: use flash loan to amplify reentrancy. Borrow massive amount → trigger reentrancy → the re-entry exploits state that was manipulated by the borrowed funds.

## Pattern #4: TWAP Oracle Multi-Block

**Severity**: HIGH

Even TWAP can be manipulated if the attacker controls consecutive blocks. This requires validator collusion or MEV-boost manipulation. Rare but possible for high-value targets.

---

*Next: Chapter 5 — Oracle Manipulation*
