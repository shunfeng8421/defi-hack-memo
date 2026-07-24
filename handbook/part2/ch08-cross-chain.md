# Chapter 8: Cross-Chain Vulnerabilities

*"A bridge is a contract that says: 'I saw something happen on another chain that I cannot verify.'"*

---

## The $152 Million Typo

On August 1, 2022, the Nomad bridge lost $152 million. The vulnerability was not a complex cryptographic flaw. It was not a validator collusion attack. It was a single line of code that should have been a different line of code.

Nomad's message verification contract contained a function that verified Merkle proofs for cross-chain messages. During a routine upgrade, a developer changed one line:

```
// Old (correct):    require(committedRoot != bytes32(0))
// New (buggy):      require(committedRoot == bytes32(0))
```

This one-character change inverted the logic. The verification function now accepted *every* message as valid. Any address could submit any cross-chain message — "transfer 100 ETH from Nomad to me" — and the bridge would execute it without question.

Within hours, hundreds of independent actors had drained the bridge. Many of them were not sophisticated attackers. They were regular users who saw the transaction on Etherscan, copied the calldata, changed the recipient address to their own, and submitted it. The bridge had become an ATM with no PIN.

The Nomad exploit is the defining case study of cross-chain security because it demonstrates the fundamental challenge: **a bridge cannot independently verify what happened on the other chain.** It can only verify that someone — a validator, a relayer, a Merkle proof — claims something happened. The security of the bridge is the security of the weakest link in that verification chain.

---

## Pattern #17: Cross-Chain Replay Attack

**Severity**: CRITICAL
**Real cases**: Multiple bridge exploits across L2s

### The Vulnerability

A signed message is processed on Ethereum. The same signed message is also valid on Polygon. And Arbitrum. And Base. Because the signature does not include a `chainId`.

```solidity
// ❌ VULNERABLE: No chainId in signed message
bytes32 hash = keccak256(abi.encode(
    MESSAGE_TYPEHASH,
    recipient,
    amount,
    nonce,
    deadline
    // Missing: chainId
));
```

### The Attack

1. User signs a message to withdraw 100 USDC from the bridge on Ethereum
2. Attacker observes the signed message (mempool, or after confirmation)
3. Attacker submits the same signed message on Polygon → bridge executes the withdrawal on Polygon
4. Attacker submits the same message on Arbitrum → bridge executes again
5. One signature. Unlimited withdrawals. Every chain that processes the message loses funds.

### The Fix

Include `chainId` and ensure it is verified:

```solidity
// ✅ SAFE: chainId included and validated
bytes32 hash = keccak256(abi.encode(
    MESSAGE_TYPEHASH,
    recipient,
    amount,
    nonce,
    deadline,
    block.chainid  // Prevents cross-chain replay
));
```

The `block.chainid` is a built-in Solidity global that returns the chain's unique identifier (1 for Ethereum, 137 for Polygon, 42161 for Arbitrum). A valid signature on Ethereum cannot be replayed on Polygon because the `chainId` differs and the hash will not match.

---

## Pattern #18: Bridge Arbitrary Call Execution

**Severity**: CRITICAL

### The Vulnerability

A bridge accepts user-supplied calldata and executes it on the destination chain. The bridge assumes the calldata is a legitimate transfer. The attacker provides calldata that drains the bridge.

```solidity
// ❌ VULNERABLE: Executes any user-supplied calldata
function executeMessage(bytes calldata data) external {
    (bool success,) = target.call(data);  // Whatever the user wants
    require(success);
}
```

### The Attack

1. Bridge receives a message from Chain A: "execute this on Chain B"
2. The message contains calldata
3. Attacker crafts calldata: `transfer(attacker, allBridgeFunds)`
4. Bridge dutifully executes the calldata → funds drained

### The Fix

The bridge must validate *what* the calldata does, not just *that* it executes:

```solidity
// ✅ SAFE: Only executes known function signatures
function executeMessage(bytes4 selector, address token, address to, uint256 amount) external {
    require(selector == TOKEN_TRANSFER_SELECTOR, "Invalid selector");
    IERC20(token).transfer(to, amount);
}
```

Never let the user control the entire calldata. Constrain the function selector and parameters to a fixed set of allowed operations.

---

## Pattern #19: Message Verification Bypass

**Severity**: CRITICAL
**Real case**: Nomad $152M

### The Vulnerability

The bridge's message verification can be bypassed. This can happen through:

1. **Logic inversion** (Nomad): `!=` became `==`
2. **Missing validation**: No check that the message was actually signed by validators
3. **Merkle proof forgery**: Incorrect leaf construction allows attacker to prove a fake message is in the tree
4. **Signature replay**: Valid message replayed after the fact

### The Attack (Merkle Proof Forgery)

A Merkle proof verifies that a specific value is in a Merkle tree by providing a path of sibling hashes from the leaf to the root. If the leaf construction is flawed, an attacker can construct a proof for a message they were never authorized to submit.

```solidity
// ❌ VULNERABLE: Leaf hash does not include the message content
bytes32 leaf = keccak256(abi.encodePacked(index));  // Only index!
// Attacker can prove ANY message exists at any index
```

### The Fix

```solidity
// ✅ SAFE: Leaf hash includes the full message
bytes32 leaf = keccak256(abi.encodePacked(
    index,
    message.sender,
    message.recipient,
    message.amount,
    message.nonce,
    message.sourceChainId
));
```

---

## Pattern #20: Validator Collusion

**Severity**: CRITICAL
**Real case**: Ronin Bridge $625M

### The Vulnerability

A bridge requires M-of-N validator signatures. If the threshold M is too low, or if the validators share infrastructure, the threshold becomes meaningless.

Ronin Bridge used a 5-of-9 validator set. Five validators were controlled by Sky Mavis (the developer). The attacker compromised Sky Mavis's infrastructure and the single independent validator they had delegated to. With five signatures, the attacker could authorize any withdrawal.

### The Fix

Validator diversity matters more than validator count:

```solidity
// ❌ VULNERABLE: No diversity requirement
require(signatures.length >= 5);

// ✅ SAFE: Geographic, organizational, and jurisdictional diversity
require(signatures.length >= 5);
require(uniqueJurisdictions(signers) >= 3);
require(uniqueOrganizations(signers) >= 3);
```

---

## The Cross-Chain Security Checklist

1. **Every signed message includes chainId.** No exceptions.
2. **User-supplied calldata is never executed directly.** Only known function selectors.
3. **Merkle proofs include the full message in the leaf.** Not just an index.
4. **Validator threshold requires organizational diversity.** Not just numeric count.
5. **Failed messages have a recovery path.** Never permanently locked.
6. **Upgrades have a timelock.** Never instant, never single-key.

---

*Next: Chapter 9 — Reentrancy & Callbacks*
