# Chapter 12: Governance Attacks

*"Democracy works when votes are expensive. Flash loans made them free."*

---

## The Beanstalk Exploit: April 17, 2022

At 07:24 UTC on April 17, 2022, an attacker submitted a governance proposal to the Beanstalk protocol. The proposal was elegantly simple: transfer all protocol funds to an address controlled by the proposer.

The attacker did not own enough BEAN tokens to pass the vote. BEAN had a market capitalization of approximately $100 million. To acquire 67% of the voting power—the threshold required by Beanstalk's governance—an attacker would need to buy $67 million worth of tokens on the open market, driving the price up with each purchase. Traditional governance assumed this cost of corruption was prohibitively high.

But the attacker did not buy the tokens. They borrowed them.

A single transaction borrowed 350 million BEAN tokens—75% of the total supply—from Aave's lending pool. The fee for this loan was approximately $3,000. Now holding a supermajority of voting power, the attacker:

1. Submitted an emergency governance proposal to transfer all protocol funds
2. Voted "yes" with 350 million BEAN tokens
3. Called the execution function

Thirteen seconds elapsed from the first function call to the final transfer. The Beanstalk treasury—$76 million in BEAN, $106 million in other assets, $182 million total—was transferred to the attacker in a single atomic transaction. The flash loan was repaid. The attacker's profit was approximately $76 million after accounting for the BEAN tokens that became worthless when the protocol collapsed.

The Beanstalk exploit was not a governance hack. It was a governance design failure. Every mechanism worked exactly as intended. The voting process was fair. The proposal was legitimate. The execution was authorized. The protocol did what it was designed to do when a supermajority of token holders voted to transfer the treasury. The problem was that "token holder" and "person with a long-term interest in the protocol's success" were no longer the same thing.

### The Aftermath

Beanstalk did not recover. The BEAN token lost 99% of its value. The protocol's code still exists on-chain—it was not hacked—but the economic trust that sustained it was destroyed. Users who had deposited funds into Beanstalk's liquidity pools received nothing. There was no insurance fund, no bailout, no Ronin-style reimbursement from a well-capitalized parent company.

The lesson Beanstalk taught the industry is that governance cannot be retrofitted onto a token that already trades on lending markets. If your governance token can be flash-loaned, your governance can be flash-loaned. The cost of corruption is not the market cap of the token. It is the flash loan fee.

---

## The Governance Attack Surface

Governance is not a single vulnerability pattern. It is a category of attack surfaces that arise from the gap between who *should* control a protocol and who *actually* controls it:

1. **Token-weighted voting**: Assumes token holders are aligned with long-term protocol health. Flash loans break this assumption by making token holding zero-commitment.

2. **Delegation**: Assumes delegates act in the interest of those who delegated to them. Delegates can be compromised, bribed, or simply negligent.

3. **Timelocks**: Assume the community has time to review and exit before execution. Attackers can front-run the execution after the timelock expires.

4. **Multi-sigs**: Assume N-of-M means distributed trust. If the signers share infrastructure, employer, or jurisdiction, N-of-M collapses to 1-of-1.

---

## Pattern #31: Flash Loan Governance Attack

**Severity**: CRITICAL
**Real case**: Beanstalk $182M

### The Attack

The complete attack sequence:

1. **Identify** a protocol where governance uses token-weighted voting, and the governance token is available on a lending market (Aave, Compound, or a DEX with flash swap support).
2. **Borrow** a supermajority of the governance token via flash loan. Most protocols require 50%+ to pass a proposal. Beanstalk required 67%.
3. **Propose** a governance action that transfers protocol funds or upgrades the implementation to a malicious version.
4. **Vote** with the borrowed tokens. The voting contract checks `balanceOf(attacker) >= quorum`. The flash-loaned balance satisfies the check.
5. **Execute** immediately if there is no timelock. If there is a timelock, wait and execute when it expires. The flash loan can be repaid after the vote because only the vote requires the tokens.
6. **Repay** the flash loan and keep the proceeds.

The entire attack costs gas plus the flash loan fee. For Beanstalk, that was approximately $3,000 against a $182 million return.

### Why Timelocks Are Insufficient

A common defense: "we have a 48-hour timelock, so flash loan governance attacks are impossible." The attacker cannot hold a flash loan for 48 hours.

This is correct but incomplete. The attacker needs the tokens for the *vote*, not the execution. Once the proposal passes, the attacker repays the flash loan. The proposal sits in the timelock. When the timelock expires, the attacker submits the execution transaction.

The timelock only delays the attack. It does not prevent it. For the timelock to work, the community must detect the malicious proposal and exit before execution. This requires:
- Active monitoring of all governance proposals
- Understanding of what each proposal does
- Willingness to withdraw funds before the proposal executes

Most DeFi users do none of these things.

### The Fix: Voting Power Snapshots

Voting power must reflect token holdings at the time of proposal creation, not at the time of voting:

```solidity
// ❌ VULNERABLE: Current balance determines voting power
function getVotes(address account) public view returns (uint256) {
    return token.balanceOf(account);
    // Flash loan inflates this to pass any vote
}

// ✅ SAFE: Historical balance at snapshot
function getVotes(address account, uint256 proposalId) public view returns (uint256) {
    return votes[account][proposalSnapshot[proposalId]];
    // Snapshot was taken when proposal was created
    // Tokens acquired after creation have zero voting power
}
```

For the snapshot to work:
1. The proposal creator must hold the required voting power BEFORE creating the proposal
2. The snapshot is taken at proposal creation time
3. Subsequent token acquisitions do not affect voting power on existing proposals

This means the attacker must hold the tokens before the proposal exists, which requires either:
- Actually buying the tokens (real cost of corruption)
- Having advance knowledge that a proposal will be created (impossible if proposal creation is permissionless)
- Creating the proposal themselves while holding the tokens

The last case is still possible—the attacker can acquire tokens, create a proposal, and sell the tokens. But this imposes a real cost: the tokens must be held between acquisition and proposal creation, and selling them after may move the market. The flash loan attack is closed.

---

## Pattern #32: Timelock Front-Running

**Severity**: HIGH

### The Attack

A malicious proposal passes the vote and enters a 48-hour timelock. The community has 48 hours to review and exit. The attacker waits.

At exactly T+48 hours, the attacker submits the execution transaction with maximum gas priority. The transaction confirms in the next block. No user can withdraw their funds between the timelock expiring and the execution confirming.

### The Fix

The execution window should be a range, not a point:

```solidity
function execute(uint256 proposalId) external {
    require(block.timestamp >= timelock[proposalId], "Too early");
    require(block.timestamp <= timelock[proposalId] + 24 hours, "Expired");
    // If not executed within 24 hours of the timelock expiring, the proposal fails.
    _execute(proposalId);
}
```

This prevents the attacker from waiting indefinitely for a favorable block. It also creates a 24-hour window where anyone—including users who want to exit—can submit the execution transaction. The attacker cannot monopolize the execution slot.

---

## Pattern #33: Hidden Owner Backdoor

**Severity**: CRITICAL

### The Vulnerability

A protocol advertises "community governance" but retains a single-key emergency function:

```solidity
function emergencyWithdraw(address token) external onlyOwner {
    IERC20(token).transfer(owner, IERC20(token).balanceOf(address(this)));
}
```

This function is the governance equivalent of a backdoor. The developer explains it as "necessary for emergencies." The attacker sees it as "one key from total control."

### The Fix

If emergency functions must exist, they must match the claimed governance structure:

```solidity
function emergencyWithdraw(address token, uint256 maxAmount) external onlyEmergencyDAO {
    require(maxAmount <= totalValueLocked * 5 / 100, "Maximum 5%");
    require(block.timestamp >= lastEmergency + 7 days, "Weekly limit");
    lastEmergency = block.timestamp;
    IERC20(token).transfer(treasury, maxAmount);
}
```

The emergency function is now governed by the DAO, not a single key. The blast radius is proportional—5% per week, not 100% per transaction. The protocol can still respond to emergencies without creating a single point of failure.

---

## The Governance Checklist

1. **Voting power is snapshotted at proposal creation time.** Current balances are never used directly.
2. **Governance tokens that can be flash-loaned have additional safeguards.** Minimum holding period, quadratic voting, or absolute vote caps.
3. **Timelocks have a bounded execution window.** Proposals expire if not executed promptly, preventing indefinite waiting.
4. **Multi-sigs require organizational diversity.** N-of-M is not sufficient if signers share employers or jurisdictions.
5. **Emergency functions are governed by the same process they claim to serve.** No single-key backdoors, no matter how "emergency" the function.

---

## Connection to Other Chapters

- **Ch4 (Flash Loans)**: The Beanstalk attack could not exist without flash loans. This is the most dangerous cross-chapter combination in the entire book. Flash loans + governance = instant protocol takeover.
- **Ch6 (Access Control)**: Governance is access control at the organizational level. Multi-sig social engineering (Ronin) is access control failure applied to humans instead of code.
- **Ch8 (Cross-Chain)**: Bridge validators are a governance structure. Validator centralization is governance centralization.

---

## Part II Summary

Part II has covered 37 patterns across 10 chapters, from flash loans to governance attacks. Every pattern has been validated against real-world exploits totaling billions of dollars in losses. Every pattern has a specific, actionable fix.

Part III shifts focus to a different execution environment entirely: Solana. The vulnerabilities are different. The defenses are different. The lesson is the same: **understand what your platform assumes, because attackers will violate every assumption they can find.**

---

*Next: Part III — Solana Security*
