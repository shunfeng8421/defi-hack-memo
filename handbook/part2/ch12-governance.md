# Chapter 12: Governance Attacks

*"Democracy works when votes are expensive. Flash loans made them free. The cost of corrupting a protocol is no longer the market cap of its token—it is the flash loan fee."*

---

## The Beanstalk Exploit: April 17, 2022

Beanstalk was a decentralized stablecoin protocol built on Ethereum. Its stablecoin, BEAN, used an algorithmic mechanism inspired by seigniorage shares—the idea that a protocol can issue and redeem tokens to maintain a price peg, much like a central bank manages a currency. Unlike most stablecoins, BEAN was not backed by collateral. It was backed by the protocol's ability to expand and contract supply in response to market demand.

The protocol's governance worked like every other DeFi governance system in 2022: BEAN holders voted on proposals proportional to their holdings. To pass an emergency proposal, the protocol required 67% of outstanding BEAN tokens to vote in favor. The assumption was that accumulating 67% of a $100 million token would cost at least $67 million—more than the protocol's treasury, making the attack economically irrational.

On April 17, 2022, an attacker proved this assumption wrong. They did not buy BEAN tokens. They borrowed them.

A single transaction, submitted at 07:24 UTC, executed the following sequence:

1. **Flash loan**: Borrow 350 million BEAN tokens (75% of total supply) from Aave's BEAN lending pool. Flash loan fee: approximately $3,000.

2. **Propose**: Create an emergency governance proposal to transfer all protocol funds to the attacker's address. Beanstalk's governance contract accepted the proposal because the proposer held 350 million BEAN.

3. **Vote**: Vote "yes" with the borrowed BEAN. `getPriorVotes(attacker, proposalSnapshot)` returned 350 million—well above the 67% threshold.

4. **Execute**: Call `execute()` on the proposal. Beanstalk's emergency proposals had no timelock. The execution was immediate.

5. **Transfer**: The proposal code transferred the entire protocol treasury—$76 million in BEAN and $106 million in other assets—to the attacker.

6. **Repay**: Return the 350 million BEAN to Aave, plus the $3,000 fee.

Thirteen seconds from the first function call to the final transfer. $182 million extracted. Flash loan repaid. The entire attack fit in a single Ethereum block.

Beanstalk did not have a bug. Every mechanism worked exactly as designed. The governance contract verified the proposer's token balance. The voting contract verified the vote weight. The execution contract verified the proposal had passed. Every check passed. Every function returned true.

The vulnerability was not in the code. It was in the assumption that "token holder" and "long-term stakeholder" are the same thing. Flash loans severed that connection. A token holder with 75% of the supply and a holding period of thirteen seconds is not a stakeholder. But the code could not tell the difference.

### The Aftermath

Beanstalk's BEAN token collapsed from $1 to less than $0.01 within hours. The protocol never recovered. Users who had deposited funds into Beanstalk's liquidity pools received nothing. There was no insurance fund. No venture capital bailout. No reimbursement.

The Beanstalk team attempted a relaunch several months later under the name "Beanstalk Farms," with a revised governance model that checkpointed voting power at the start of each "season" (roughly every hour). But the damage to trust was permanent. The relaunched protocol attracted a fraction of the original TVL.

The lesson Beanstalk taught the industry is stark and simple: **governance cannot be retrofitted onto a token that already trades on lending markets.** If your governance token can be flash-loaned, your governance can be flash-loaned. The cost of corruption is not the market cap—it's the flash loan fee. And the flash loan fee for a $182 million treasury was $3,000.

---

## The Ronin Bridge: Validator Governance Failure

On March 23, 2022, the Ronin bridge—the cross-chain bridge connecting the Ronin sidechain to Ethereum mainnet, built for the Axie Infinity game by Sky Mavis—was drained of 173,600 ETH and 25.5 million USDC. Total value: approximately $625 million.

The attack was not a smart contract vulnerability. The bridge contracts functioned correctly. The validation logic worked as designed. The vulnerability was in the governance that controlled the validators.

Ronin used a 5-of-9 multi-signature scheme for bridge withdrawals. Of the 9 validator keys:

- 4 were controlled by Sky Mavis (the game developer)
- 1 was controlled by the Axie DAO
- 4 were controlled by external validators

The 4 Sky Mavis keys were not independently managed. Three of them shared the same infrastructure and access controls. One had been granted to the Axie DAO months earlier for a one-time transaction but was never revoked.

In December 2021, Sky Mavis asked the Axie DAO to whitelist a specific address for a gas-free RPC node. The DAO approved the request. The approval gave the gas-free RPC node the authority to sign transactions as a validator. Sky Mavis never revoked this approval.

In March 2022, the attacker:

1. Compromised the gas-free RPC node's signing key (the fourth Sky Mavis key, still active from the December transaction)
2. Obtained the Axie DAO validator key (the fifth key, also from the December transaction)
3. Controlled both through the same compromised infrastructure

Now holding 5 of 9 validator keys, the attacker submitted a withdrawal transaction for 173,600 ETH and 25.5M USDC. The bridge's multi-sig verified: 5 of 9 signatures present. Transaction approved. Funds transferred.

The bridge was not hacked. The multisig was not broken. The governance that managed the multisig failed—keys that were supposed to be independent were shared. Approvals that were supposed to be temporary were permanent. Validators that were supposed to be distributed were controlled by the same entity.

Ronin and Beanstalk are the same story told twice. Beanstalk's governance failed because tokens could be borrowed. Ronin's governance failed because keys could be consolidated. In both cases, the code was correct. The assumptions were not.

---

## The Governance Attack Surface

Governance is not a single vulnerability pattern. It is a category of attack surfaces that arise from five fundamental gaps:

1. **Token-weighted voting**: Assumes token holders act in the protocol's long-term interest. Flash loans break this by making token holding zero-commitment. A holder for 13 seconds has the same vote as a holder for 13 months.

2. **Delegation**: Assumes delegates act for those who delegated to them. Delegates can be compromised, bribed (Dark DAOs), or negligent. The protocol has no mechanism to verify that a delegate's vote reflects their delegators' preferences.

3. **Timelocks**: Assume the community detects malicious proposals before execution. Detection requires active monitoring that most users do not perform. A proposal that passes at 3 AM UTC on a Saturday may execute before anyone notices.

4. **Multi-sigs**: Assume N-of-M means distributed trust. If signers share infrastructure, employer, or jurisdiction, N-of-M collapses to 1-of-1. Ronin proved this with $625 million at stake.

5. **Protocol-owned liquidity**: Assume the protocol controls its treasury. If governance can be captured, the treasury is the attacker's exit liquidity. Beanstalk proved this with $182 million.

---

## Pattern #31: Flash Loan Governance Attack

**Severity**: CRITICAL
**Real case**: Beanstalk $182M (2022)
**Also**: Multiple smaller protocols in 2022-2023

### The Attack

```solidity
// ❌ VULNERABLE: Current balance determines voting power
contract VulnerableGovernor {
    IERC20 public governanceToken;
    
    function propose(bytes calldata actions) external returns (uint256) {
        require(
            governanceToken.balanceOf(msg.sender) >= proposalThreshold,  // ← flash-loanable!
            "Insufficient tokens"
        );
        // Creates proposal...
    }
    
    function castVote(uint256 proposalId, bool support) external {
        uint256 weight = governanceToken.balanceOf(msg.sender);  // ← flash-loanable!
        proposals[proposalId].votes[support ? 0 : 1] += weight;
    }
}
```

The attacker flash-loans the governance token for a single transaction. The borrow, propose, vote, execute, and repay all occur atomically. The protocol never sees a long-term holder—it sees a balance at a specific block, and that balance is sufficient.

### Why Timelocks Are Insufficient

A common defense: "we have a 48-hour timelock, so flash loan attacks are impossible—the attacker cannot maintain a flash loan for 48 hours."

This is correct about the loan duration and incorrect about the attack. The attacker needs the tokens for the *vote*, not the execution. Once the vote passes, the attacker repays the flash loan. The proposal waits in the timelock. When the timelock expires, the attacker submits the execution transaction—no tokens required.

For the timelock to actually prevent the attack, two things must happen:

1. **The community detects the malicious proposal.** This requires monitoring infrastructure, which most protocols do not provide and most users do not run.

2. **Users withdraw their funds before execution.** This requires users to trust that the proposal is actually malicious, which requires understanding Solidity code—a skill most DeFi users lack.

Neither condition is reliably met. The timelock delays the attack. It does not prevent it.

### The Fix: Snapshot Voting with Holding Period

```solidity
// ✅ SAFE: Voting power is checkpointed at proposal creation
contract SecureGovernor {
    IERC20 public governanceToken;
    mapping(uint256 => mapping(address => uint256)) public votes;
    
    // Snapshot voting power at proposal creation time
    function propose(bytes calldata actions) external returns (uint256 proposalId) {
        uint256 snapshotBlock = block.number;
        uint256 votingPower = governanceToken.getPriorVotes(
            msg.sender, 
            snapshotBlock - 1  // Must have held tokens BEFORE proposal creation
        );
        require(votingPower >= proposalThreshold, "Insufficient voting power");
        
        proposalId = _createProposal(actions, snapshotBlock);
        votes[proposalId][msg.sender] = votingPower;
    }
    
    // Voting power is fixed at proposal creation snapshot
    function castVote(uint256 proposalId, bool support) external {
        uint256 weight = votes[proposalId][msg.sender];
        // This was checkpointed when the proposal was created
        // Tokens acquired after creation have zero weight
        _recordVote(proposalId, msg.sender, support, weight);
    }
}
```

The attacker must now hold the tokens **before** creating the proposal, which cannot happen atomically with a flash loan. The tokens must be held across at least one block boundary. This imposes a real cost—market risk, opportunity cost, price impact—that makes the attack economically expensive even without buying the tokens outright.

For additional protection, add a minimum holding period:

```solidity
require(
    governanceToken.getPriorVotes(msg.sender, snapshotBlock - MIN_HOLDING_BLOCKS) >= proposalThreshold,
    "Tokens not held long enough"
);
// MIN_HOLDING_BLOCKS = ~1 week of blocks
```

This ensures voting power reflects long-term holdings, not short-term accumulation.

---

## Pattern #32: Multi-Sig Centralization

**Severity**: CRITICAL
**Real case**: Ronin Bridge $625M (2022), Harmony Bridge $100M (2022)

### The Vulnerability

A protocol advertises "decentralized governance" but its key management is centralized:

```
Validator Key 1: Sky Mavis infra
Validator Key 2: Sky Mavis infra  ← same organization
Validator Key 3: Sky Mavis infra  ← same organization
Validator Key 4: Sky Mavis infra  ← same organization (gas-free RPC node)
Validator Key 5: Axie DAO         ← approved for temp access, never revoked
```

Five of nine keys controlled by effectively one entity. The "5-of-9" multisig was actually "1-of-1" control distributed across different key files.

### Detection

Audit the key management, not just the smart contracts:

```
□ Are all multi-sig signers from different organizations?
  If two signers work for the same company, they are one signer.

□ Are old access grants revoked?
  Axie DAO's temporary gas-free RPC approval remained active for 4 months.

□ Are keys stored on different infrastructure?
  Three Sky Mavis keys on the same compromised server.

□ Does the protocol have a key rotation policy?
  Keys that remain static for years are keys that attackers have time to target.

□ Can compromised keys be replaced without protocol downtime?
  If not, every key compromise is a protocol freeze.
```

### The Fix: Organizational Diversity + Rotation

```solidity
// Key management considerations (not code-enforceable—process-enforced):
//
// 1. Each signer MUST be from a different legal entity
// 2. Signers MUST rotate every 90 days
// 3. Temporary access grants MUST have automatic expiration
// 4. No signer may control more than one key
// 5. Key compromise procedures must be tested quarterly
```

The governance contract cannot enforce organizational diversity. That is a human process problem. But the contract CAN enforce minimum time between signer changes:

```solidity
mapping(address => uint256) public lastRotation;

function rotateSigner(address oldSigner, address newSigner) external onlyMultisig {
    require(
        block.timestamp >= lastRotation[oldSigner] + 90 days,
        "Signer rotation too frequent"
    );
    // But a signer that hasn't rotated in 180 days should trigger an alert
    require(
        block.timestamp <= lastRotation[oldSigner] + 180 days,
        "Signer rotation required"
    );
    _removeSigner(oldSigner);
    _addSigner(newSigner);
    lastRotation[newSigner] = block.timestamp;
}
```

---

## Pattern #33: Hidden Owner Backdoor

**Severity**: CRITICAL
**Real case**: Multiple "community-governed" protocols with single-key emergency functions

### The Vulnerability

A protocol advertises "decentralized governance" but retains administrative functions controlled by a single key:

```solidity
address public owner;  // Single EOA, supposedly the "protocol administrator"

function emergencyWithdraw(address token) external onlyOwner {
    IERC20(token).transfer(owner, IERC20(token).balanceOf(address(this)));
    // One transaction. Entire treasury. No multisig. No timelock.
}

function upgradeTo(address newImpl) external onlyOwner {
    _upgradeTo(newImpl);
    // Replace entire protocol logic with attacker's code
}
```

These functions are explained as "necessary for emergencies—we'll renounce ownership once the protocol is stable." The protocol is never "stable enough." Ownership is never renounced. The backdoor remains, controlled by one key, for the protocol's entire lifetime.

### The Fix

If emergency functions exist, they must match the governance structure the protocol claims:

```solidity
contract GovernedEmergency {
    uint256 public constant MAX_WITHDRAWAL_BPS = 500;  // 5%
    uint256 public constant EMERGENCY_COOLDOWN = 7 days;
    uint256 public lastEmergency;
    
    function emergencyWithdraw(
        address token,
        uint256 maxAmount
    ) external onlyGovernance {  // Governance vote, not single key
        require(
            maxAmount <= totalValueLocked * MAX_WITHDRAWAL_BPS / 10_000,
            "Exceeds maximum emergency withdrawal"
        );
        require(
            block.timestamp >= lastEmergency + EMERGENCY_COOLDOWN,
            "Emergency cooldown not elapsed"
        );
        lastEmergency = block.timestamp;
        IERC20(token).transfer(treasury, maxAmount);
    }
}
```

The emergency function is now governed by the DAO. The blast radius is limited—5% per week, not 100% per transaction. The protocol can respond to emergencies while maintaining the governance guarantees it advertises to users.

---

## The Governance Checklist

```
□ Voting power is snapshotted at proposal creation, not voting time.
  Current balances are never used directly. Flash loans are neutralized.

□ Governance tokens with lending market liquidity have holding period requirements.
  A token held for 13 seconds is not a stakeholder. Minimum: 1 week.

□ Timelocks have bounded execution windows.
  Proposals that sit in the timelock forever are proposals waiting to be executed during a
  Saturday night when nobody is watching.

□ Multi-sig signers are from different organizations.
  Not different people. Different organizations. Two employees of the same company count as one.

□ Emergency functions use the same governance as normal functions.
  No single-key backdoors, no matter how "emergency" the function's name.

□ Temporary access grants have automatic expiration.
  Ronin's Axie DAO key was temporary. It remained active for 4 months.

□ All admin keys are documented and their holders are publicly known.
  Undocumented admin keys are backdoors. Period.
```

---

## Connection to Other Chapters

- **Ch4 (Flash Loans)**: The Beanstalk attack is the canonical combination of flash loans and governance failure. Without flash loans, the attack economy collapses. Flash loans enable instant token accumulation; governance enables instant protocol control.

- **Ch6 (Access Control)**: Governance IS access control at the organizational level. Ronin's multi-sig failure is the same pattern as a contract's `onlyOwner` modifier controlled by a compromised key. The difference is scale: one compromised key controls all keys.

- **Ch8 (Cross-Chain)**: Bridge validators are governance validators. Validator centralization is governance centralization applied to cross-chain message verification. Ronin teaches both lessons simultaneously.

- **Ch10 (Initialization)**: The "hidden owner" backdoor (Pattern #33) and the "uninitialized implementation" attack (Pattern #21) are the same vulnerability: a function that should be inaccessible but isn't. Governance backdoors are initialization errors that persist.

---

## Part II: Closing

Part II has covered the core attack patterns of DeFi across 9 chapters, from flash loans (Ch4) to governance (Ch12). Every pattern in this section has been validated against real-world exploits totaling billions of dollars in losses. Every pattern has a specific, actionable fix.

The patterns share a common thread: **protocols fail not because they are hacked, but because their assumptions about attacker behavior, market conditions, and user incentives are violated.** Flash loans violate the assumption that capital is expensive. Oracle manipulation violates the assumption that prices are trustworthy. Reentrancy violates the assumption that external calls are safe. Governance attacks violate the assumption that token holders are stakeholders.

Part III shifts to Solana—a different execution environment with different assumptions, different vulnerabilities, and different defenses. The platform changes. The lesson does not: understand your assumptions, because attackers will violate every one of them.

---

*Next: Part III — Solana Security*
