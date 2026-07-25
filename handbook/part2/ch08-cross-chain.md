# Chapter 8: Cross-Chain Vulnerabilities

*"A bridge is a contract that says: 'I saw something happen on another chain that I cannot verify.' Every word in that sentence is a vulnerability."*

---

## The Nomad Incident

At 21:32 UTC on August 1, 2022, the Nomad token bridge—a cross-chain protocol holding $190 million in user assets—processed a routine upgrade to its Replica contract. The upgrade changed one line of code in the message verification function.

The old line:
```solidity
require(committedRoot != bytes32(0), "Invalid root");
```

The new line:
```solidity
require(committedRoot == bytes32(0), "Invalid root");
```

One character. `!=` became `==`. The logic inverted. A function that was supposed to reject messages without a valid Merkle root was now accepting every message that lacked one. Since new roots started as `bytes32(0)` before being initialized, every uninitialized message path was now valid.

The upgrade was deployed at 21:32. By 21:34, the first exploit transaction was confirmed. By 21:45, dozens of independent actors were draining the bridge. By midnight, $152 million was gone.

What makes Nomad unique among bridge exploits is how many people participated. The first attacker was sophisticated—they understood the bug, crafted the calldata, and submitted a transaction that drained millions. But within minutes, Etherscan showed the transaction. Users copied the calldata, changed the recipient address to their own wallet, and submitted identical transactions. The bridge had become an ATM where anyone who knew the PIN could withdraw. The PIN was public.

### The Deeper Failure

Nomad's vulnerability was not the `!=` to `==` error. That was the triggering condition. The vulnerability was the absence of a defense-in-depth architecture that would have caught the error before deployment.

A well-designed bridge has multiple independent verification layers:

1. **Format validation**: Is the message correctly structured?
2. **Signature verification**: Was the message signed by the required number of validators?
3. **Merkle proof verification**: Does the message exist in the committed state tree?
4. **Replay protection**: Has this message already been processed?
5. **Value constraint**: Is the amount being transferred within acceptable bounds?

Nomad's bug broke layer 3—the Merkle proof verification. Every subsequent layer should have caught the error. A correctly-formatted message with a valid Merkle proof should still have required validator signatures and passed replay protection checks. But Nomad, like many bridges, had designed these layers as sequential rather than parallel. If layer 3 passed, layers 4 and 5 were never checked.

The lesson: **bridge security must be defense-in-depth, not defense-in-sequence.** Every verification layer must operate independently. Failure of one layer must never cascade into failure of all layers.

---

## Why Bridges Are Different

A bridge is not a standalone protocol. It is a distributed system that spans at least two independent blockchains. This architectural reality creates attack surfaces that do not exist in single-chain protocols:

1. **Trust asymmetry**: The source chain cannot verify what happens on the destination chain. Every bridge relies on some form of intermediary—validators, relayers, oracle networks—to attest to cross-chain events.

2. **State fragmentation**: The total state of the bridge is split across multiple chains. An attacker who compromises one chain's bridge contract may be able to drain assets on another chain where the bridge has already credited them.

3. **Upgrade complexity**: Every bridge upgrade must be coordinated across multiple chains, deployed in the correct sequence, and verified for compatibility. Nomad's one-character error occurred during one such upgrade.

4. **Liquidity concentration**: Bridges hold large amounts of assets on multiple chains simultaneously. A successful exploit on one chain can drain assets from every chain.

The hardening gradient applies to bridges with particular severity. Large bridges (Wormhole, LayerZero) have survived attacks that would have destroyed smaller bridges. But when a large bridge fails—as Ronin did for $625 million—the damage is catastrophic.

---

## Pattern #17: Cross-Chain Replay Attack

**Severity**: CRITICAL
**Real cases**: Multiple L2 bridge exploits

### The Vulnerability

A signed message is valid on Ethereum. The same signed message is also valid on Polygon, Arbitrum, Optimism, and Base. Because the signature does not include a `chainId`.

```solidity
// ❌ VULNERABLE: No chainId in signed message
bytes32 hash = keccak256(abi.encode(
    MESSAGE_TYPEHASH,
    recipient,
    amount,
    nonce,
    deadline
    // Missing: block.chainid
));
address signer = ecrecover(hash, v, r, s);
require(signer == expectedSigner, "Invalid signature");
```

The signature verification succeeds on every chain. The `nonce` is chain-specific, so it appears unique on each chain. The `deadline` is in the future, so the message is not expired. Every check passes.

### The Attack

1. User signs a message to withdraw 1,000 USDC from the bridge on Ethereum mainnet
2. User submits the message on Ethereum → bridge processes the withdrawal
3. Attacker observes the signed message (mempool, or after confirmation via event logs)
4. Attacker submits the **same signed message** on Polygon → bridge has never seen this nonce on Polygon → processes the withdrawal
5. Attacker submits again on Arbitrum → bridge processes
6. Attacker submits again on Base → bridge processes
7. One signature. Four chains. Four withdrawals. The user authorized one.

### Why Nonces and Deadlines Are Not Enough

A common defense is: "we have nonces per chain, so replay is impossible." This is incorrect. Nonces prevent double-spending on the same chain. They do not prevent replay on a different chain. Each chain maintains its own nonce counter. A nonce that has been used on Ethereum has never been used on Polygon.

Similarly, deadlines only bound the time window. A deadline of "7 days from now" gives the attacker seven days to replay the signature on every available chain.

### The Fix

Include `block.chainid` in every signed message and verify it at the contract level:

```solidity
// ✅ SAFE: ChainId included and validated
bytes32 hash = keccak256(abi.encode(
    MESSAGE_TYPEHASH,
    recipient,
    amount,
    nonce,
    deadline,
    block.chainid     // <— This prevents cross-chain replay
));

address signer = ecrecover(hash, v, r, s);
require(signer == expectedSigner, "Invalid signature");

// Additionally: the contract should verify chainId at execution time
uint256 messageChainId;
assembly { messageChainId := chainid() }
require(messageChainId == block.chainid, "Wrong chain");
```

The `block.chainid` is a built-in Solidity global that returns the chain's unique identifier:
- Ethereum mainnet: 1
- Polygon: 137
- Arbitrum: 42161
- Optimism: 10
- Base: 8453

A valid signature on chain 1 will never produce a matching hash on chain 137, because the `chainId` differs and the cryptographic hash is completely different.

---

## Pattern #18: Bridge Arbitrary Call Execution

**Severity**: CRITICAL

### The Vulnerability

A bridge receives a message from its source chain saying "execute this calldata on the destination chain." The bridge executes the calldata without validating what it does. The attacker provides calldata that drains the bridge rather than transferring tokens.

```solidity
// ❌ VULNERABLE: Executes any user-supplied calldata
function executeMessage(bytes calldata data) external onlyRelayer {
    (bool success,) = target.call(data);
    // What does data do? Nobody knows. Bridge executes it anyway.
    require(success);
}
```

### The Attack

1. Attacker constructs calldata: `transfer(bridgeAddress, attackerAddress, allBridgeFunds)`
2. Attacker submits this as a cross-chain message on the source chain
3. Relayer forwards the message to the destination chain
4. Destination chain's bridge contract executes the calldata
5. All funds transferred to the attacker

The bridge assumed the calldata was a legitimate transfer. The attacker used it as a drain instruction.

### The Fix

Never execute user-supplied calldata. Restrict execution to a fixed set of known function selectors:

```solidity
// ✅ SAFE: Only known function selectors allowed
bytes4 constant TRANSFER_SELECTOR = bytes4(keccak256("transfer(address,uint256)"));
bytes4 constant MINT_SELECTOR = bytes4(keccak256("mint(address,uint256)"));

function executeMessage(
    bytes4 selector,
    address token,
    address to,
    uint256 amount
) external onlyRelayer {
    require(
        selector == TRANSFER_SELECTOR || selector == MINT_SELECTOR,
        "Invalid selector"
    );
    // Execute the specific, constrained operation
    if (selector == TRANSFER_SELECTOR) {
        IERC20(token).transfer(to, amount);
    } else {
        IMintable(token).mint(to, amount);
    }
}
```

The user no longer controls the calldata. They control the parameters to a constrained set of operations. This eliminates the ability to inject arbitrary execution.

---

## Pattern #19: Validator Collusion via Centralization

**Severity**: CRITICAL
**Real case**: Ronin Bridge $625M

### The Attack

The Ronin Bridge validator set was 5-of-9. Sky Mavis—the developer—controlled four validators directly. The Axie DAO controlled a fifth validator but had delegated its voting power to Sky Mavis for operational convenience. The remaining four validators were independent.

The attacker did not break any cryptographic keys. They socially engineered access to Sky Mavis's infrastructure. With control of Sky Mavis's systems, they gained control of five validators—four directly, one via delegation. Five signatures were sufficient to authorize any withdrawal.

Over two transactions, the attacker withdrew 173,600 ETH and 25.5 million USDC—$625 million at the time. The attack went undetected for six days. Users continued depositing funds into a bridge that had already been drained.

### The Fix

Validator diversity is not a technical requirement. It is an organizational one:

```solidity
// ✅ SAFE: Diversity enforced at the smart contract level
function verifyValidatorSet(address[] calldata signers) internal view {
    require(signers.length >= 6, "Insufficient signers");
    
    // Organizational diversity
    uint256 uniqueOrgs;
    uint256 uniqueJurisdictions;
    for (uint256 i = 0; i < signers.length; i++) {
        if (!orgSeen[validatorOrg[signers[i]]]) {
            orgSeen[validatorOrg[signers[i]]] = true;
            uniqueOrgs++;
        }
        if (!jurisdictionSeen[validatorJurisdiction[signers[i]]]) {
            jurisdictionSeen[validatorJurisdiction[signers[i]]] = true;
            uniqueJurisdictions++;
        }
    }
    require(uniqueOrgs >= 4, "Insufficient org diversity");
    require(uniqueJurisdictions >= 3, "Insufficient jurisdiction diversity");
}
```

Even if one organization is fully compromised, the remaining validators from different organizations prevent a quorum.

For protocols that cannot achieve organizational diversity, add blast radius limits:

```solidity
uint256 public constant MAX_SINGLE_WITHDRAWAL = 1000 ether;
uint256 public constant DAILY_WITHDRAWAL_CAP = 10000 ether;
uint256 public constant WITHDRAWAL_COOLDOWN = 1 hours;
mapping(bytes32 => uint256) public dailyWithdrawn;
```

---

## Pattern #20: Unverified Message Format

**Severity**: CRITICAL

### The Vulnerability

The bridge receives a cross-chain message and processes its contents without validating the message's structure. A malformed message—one with extra fields, missing fields, or wrong field types—can cause the bridge to misinterpret the sender's intent.

```solidity
// ❌ VULNERABLE: No format validation
function processMessage(bytes calldata rawMessage) external onlyRelayer {
    (address sender, address recipient, uint256 amount) = abi.decode(
        rawMessage,
        (address, address, uint256)
    );
    // If the message has 4 fields but we only decode 3, the 4th is ignored
    // If the message has 2 fields, the decode reverts
    token.transfer(recipient, amount);
}
```

### The Attack

The `abi.decode` function extracts exactly the number of fields requested. If the message has additional fields, they are silently ignored. If the message was intended to include a fee parameter that should reduce the transferred amount, the bridge ignores it and transfers the full amount.

### The Fix

Validate the message length before decoding:

```solidity
// ✅ SAFE: Message structure validated
function processMessage(bytes calldata rawMessage) external onlyRelayer {
    // Valid message format: sender(20) + recipient(20) + amount(32) = 72 bytes
    require(rawMessage.length == 72, "Invalid message length");
    
    (address sender, address recipient, uint256 amount) = abi.decode(
        rawMessage,
        (address, address, uint256)
    );
    // Additional semantic validation
    require(recipient != address(0), "Invalid recipient");
    require(amount <= maxTransferAmount, "Amount exceeds limit");
    
    token.transfer(recipient, amount);
}
```

---

## The Cross-Chain Security Checklist

1. **Every signed message includes `block.chainid`.** Never assume the signature is single-chain.
2. **Every bridge executes only known function selectors, never arbitrary calldata.**
3. **Validator sets require organizational diversity, not just numerical thresholds.**
4. **Every message is validated for structure, length, and semantic correctness before processing.**
5. **Failed messages have a recovery path.** Nomad had none. Ronin had none. Users lost everything.
6. **Upgrades are never single-key and never instant.** Multi-sig with 48-hour timelock minimum.
7. **Every verification layer operates independently.** Failure of one must never cascade.

---

## Connection to Other Chapters

- **Ch4 (Flash Loans)**: Cross-chain replay attacks can be combined with flash loans—borrow assets on Chain A, replay a signature on Chain B to drain assets, repay on Chain A.
- **Ch6 (Access Control)**: Bridge validator centralization is an access control failure. Ronin's 5-of-9 was a single point of failure disguised as distributed trust.
- **Ch10 (Initialization)**: Bridge upgrades that change verification logic (Nomad) are upgrade attacks. The `!=` to `==` error was an initialization failure.
- **Ch12 (Governance)**: Bridge validator sets are governance structures. The Beanstalk and Ronin attacks both exploited governance centralization.

---

*Next: Chapter 9 — Reentrancy & Callbacks*
