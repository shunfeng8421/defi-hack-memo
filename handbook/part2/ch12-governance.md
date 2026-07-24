# Chapter 12: Governance & Admin Attacks

*"Democracy works when votes are expensive. Flash loans made votes free."*

---

## The Beanstalk Exploit

On April 17, 2022, at 07:24 UTC, an attacker submitted a governance proposal to the Beanstalk protocol. The proposal was a single transaction: transfer all protocol funds — $182 million worth of assets, including $76 million in the protocol's own BEAN token — to an address controlled by the attacker.

The attacker did not own enough BEAN tokens to pass a governance vote. BEAN had a market cap of approximately $100 million. To acquire 67% of the voting power — the threshold to pass any proposal — an attacker would need to buy $67 million worth of tokens on the open market, driving the price up as they accumulated.

Or they could borrow them.

The attacker borrowed 350 million BEAN tokens — approximately 75% of the total supply — from Aave, for a fee of approximately $3,000. With this voting power, they submitted and passed the emergency proposal. By the time the transaction confirmed, $182 million had been transferred. The entire governance process — proposal, vote, execution — took 13 seconds.

Beanstalk is not a governance failure. It is a governance design failure. The protocol assumed that voting power was expensive to acquire. Flash loans made it free. The governance mechanism was working exactly as designed when it processed a valid proposal supported by a supermajority of token holders. The design was wrong.

---

## The Governance Attack Surface

Governance attacks exploit the gap between *who should have power* and *who actually has power.* The gap exists because:

1. **Token-weighted voting** assumes that token holders are aligned with the protocol's long-term interests. Flash loans allow non-holders to acquire voting power temporarily.
2. **Delegation** assumes that delegates act in the best interest of those who delegated to them. Delegates can be compromised, bribed, or simply negligent.
3. **Timelocks** assume that the community has time to react to malicious proposals. Attackers can front-run the execution after the timelock expires.
4. **Multi-sigs** assume that N-of-M is a meaningful threshold. If M parties share infrastructure or trust, N-of-M becomes 1-of-1.

---

## Pattern #30: Flash Loan Governance Attack

**Severity**: CRITICAL
**Real case**: Beanstalk $182M

### The Attack

1. **Identify**: Find a protocol where governance decisions are made by token-weighted voting, and the governance token is available on a lending market.
2. **Borrow**: Flash loan a supermajority of the governance token (67%+ for most DAOs).
3. **Propose**: Submit a governance proposal that transfers all protocol funds to the attacker.
4. **Vote**: Use the borrowed tokens to vote "yes" on the proposal.
5. **Execute**: Call the execution function — wait until any timelock expires if necessary.
6. **Repay**: Repay the flash loan. The proposal passes, the funds are transferred, and the tokens are returned.
7. **Result**: $182 million transferred. 13 seconds elapsed. $3,000 cost.

### Why Timelocks Are Not Enough

Many protocols believed that a governance timelock would prevent flash loan attacks. The logic: a proposal must be queued for 48 hours before execution. The attacker cannot hold the flash loan for 48 hours.

This is correct but insufficient. The attacker does not need to hold the loan through the timelock. They need to hold it through the *vote.* Once the proposal passes the vote, the attacker can repay the flash loan. The proposal sits in the timelock. When the timelock expires, the attacker executes it with their own funds.

The timelock only delays the attack. It does not prevent it.

### The Fix: Voting Power Snapshots

Voting power must be snapshotted at the time of proposal creation, not at the time of voting:

```solidity
// ❌ VULNERABLE: Current balance
function getVotes(address account) public view returns (uint256) {
    return token.balanceOf(account);  // Flash loan inflates this
}

// ✅ SAFE: Snapshot at proposal creation time
function getVotes(address account, uint256 proposalId) public view returns (uint256) {
    return votes[account][proposalSnapshot[proposalId]];  // Historical balance
}
```

The snapshot records every holder's balance at the block when the proposal was created. Tokens acquired after that block have no voting power on this proposal. A flash loan taken after the proposal exists is useless.

---

## Pattern #31: Multi-Sig Social Engineering

**Severity**: HIGH
**Real case**: Ronin Bridge $625M

### The Attack

The Ronin Bridge validator set was 5-of-9. Five validators were controlled by Sky Mavis (the developer). Four were external. The attacker did not break any cryptographic keys. They did not find a bug in the validator contract.

They socially engineered one Sky Mavis employee to approve a malicious validator set change. With five keys — the four Sky Mavis keys plus the compromised external key — the attacker authorized the withdrawal of $625 million.

### The Fix

No amount of code can prevent social engineering. But code can limit the blast radius:

```solidity
// ✅ BLAST RADIUS LIMITS
uint256 public constant MAX_SINGLE_WITHDRAWAL = 1000 ether;  // Per-transaction cap
uint256 public constant DAILY_WITHDRAWAL_LIMIT = 10000 ether;  // 24h rolling cap
uint256 public constant WITHDRAWAL_COOLDOWN = 1 hours;  // Between withdrawals
```

Even if an attacker compromises the validator set, they cannot drain the entire bridge in one transaction. The daily limit caps the damage. The cooldown provides time to react. The per-transaction cap forces the attacker to submit many transactions — increasing the chance of detection.

---

## Pattern #32: Timelock Front-Running

**Severity**: HIGH

### The Attack

A governance proposal passes the vote and enters a 48-hour timelock. During the timelock, the community can review the proposal and exit if it is malicious.

But the attacker waits. At exactly T+48 hours, they submit the execution transaction with maximum gas priority. Nobody else can get a transaction confirmed in the same block. The malicious proposal executes before any user can withdraw.

### The Fix

The execution window should be a range, not a point:

```solidity
// ✅ SAFE: Execution window with maximum delay
function execute(uint256 proposalId) external {
    require(block.timestamp >= proposalTimelock[proposalId], "Too early");
    require(block.timestamp <= proposalTimelock[proposalId] + 24 hours, "Expired");
    // If nobody executes within 24 hours of the timelock expiring, the proposal fails.
}
```

This prevents the attacker from waiting indefinitely for a favorable block. It also prevents the attacker from executing in a single block that nobody else can compete in — other users can submit execution transactions too.

---

## Pattern #33: Hidden Owner Backdoor

**Severity**: CRITICAL

### The Vulnerability

A protocol advertises itself as "governed by the community" or "fully decentralized." The contract contains a function that only the deployer can call — and that function can drain all funds.

```solidity
function emergencyWithdraw(address token) external onlyOwner {
    IERC20(token).transfer(owner, IERC20(token).balanceOf(address(this)));
    // Looks like an emergency function. Is an invitation to steal.
}
```

This pattern is more common than the industry admits. Protocols that market themselves as decentralized while retaining a single-key emergency function are deceiving their users.

### The Fix

If the emergency function must exist, it must be transparent:

```solidity
function emergencyWithdraw(address token) external onlyEmergencyDAO {
    emit EmergencyWithdrawal(token, msg.sender, amount);
    IERC20(token).transfer(emergencyTreasury, amount);
}
```

The function must be controlled by a governance process — not a single key. The function's existence must be documented. Users must know that the protocol reserves the right to move their funds in an emergency.

---

## Part II Summary: The 50 Core DeFi Patterns

### Flash Loans (Ch4)
1. Spot Price Oracle — CRITICAL
2. CEI/Reentrancy — CRITICAL
3. Flash + Reentrancy Combo — CRITICAL
4. TWAP Multi-Block — HIGH

### Oracle Manipulation (Ch5)
5. ERC-4626 Inflation — CRITICAL
6. Uniswap V2 Oracle — CRITICAL
7. Chainlink Stale — HIGH
8. Self-Reported Oracle — CRITICAL

### Access Control (Ch6)
9. Missing Access Control — HIGH
10. Admin Privilege — HIGH
11. Unprotected Selfdestruct — CRITICAL
12. Delegatecall to User — CRITICAL

### Token Economics (Ch7)
13. Fee-on-Transfer — HIGH
14. Rebase Token — HIGH
15. Mint/Burn Asymmetry — MEDIUM
16. Permit Without Nonce — MEDIUM

### Cross-Chain (Ch8)
17. Cross-Chain Replay — CRITICAL
18. Bridge Arbitrary Call — CRITICAL
19. Message Verification Bypass — CRITICAL
20. Validator Collusion — CRITICAL

### Reentrancy (Ch9)
21. Classic Reentrancy — CRITICAL
22. ERC-777 Callback — HIGH
23. Cross-Function — HIGH
24. Read-Only Reentrancy — MEDIUM

### Initialization (Ch10)
25. Unprotected Initializer — HIGH
26. Storage Collision — CRITICAL
27. Beacon Proxy Swap — HIGH
28. CREATE2 Re-deploy — HIGH

### Precision & Gas (Ch11)
29. Precision Loss — MEDIUM
30. Unsafe Downcast — MEDIUM
31. Hardcoded Gas — LOW
32. Unbounded Loop — MEDIUM
33. Phantom Fallback — MEDIUM

### Governance (Ch12)
34. Flash Loan Governance — CRITICAL
35. Multi-Sig Social Engineering — HIGH
36. Timelock Front-Run — HIGH
37. Hidden Backdoor — CRITICAL

---

**38 patterns covered. 12 more patterns cover MEV, sandwich attacks, and front-running — patterns 39-50 — to be detailed in the Domain Extensions section.**

---

*Next: Part III — Solana Security (Patterns 51-58)*
