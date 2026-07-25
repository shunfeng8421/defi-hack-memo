# Chapter 20: GameFi Economics

*"When money meets games, players optimize for profit. When profit extraction exceeds value creation, the game dies."*

---

## The Axie Infinity Death Spiral

Axie Infinity was the most successful GameFi project in history, generating over $4 billion in total trading volume. Players earned SLP tokens by playing the game. These tokens could be sold for real money. At its peak, players in the Philippines were earning more than the national minimum wage.

The problem: SLP was inflationary. Every Axie battle generated new tokens. As more players joined, more tokens were created. Supply grew faster than demand. The price fell. Players earned less. They played more to compensate—generating even more supply. The price fell further.

This is not a hack. It is math. An infinite-supply token backed by nothing will trend toward zero. Axie's tokenomics were designed for growth—if players were joining, new players would buy tokens from existing players, creating demand. When growth stopped, the entire economic model collapsed.

---

## Pattern #53: On-Chain RNG Manipulation

**Severity**: HIGH

### The Vulnerability

Games use on-chain random number generation for loot drops, card draws, and other probabilistic outcomes. On-chain RNG is predictable:

```solidity
// ❌ VULNERABLE: Deterministic RNG
uint256 random = uint256(keccak256(abi.encodePacked(
    block.timestamp,
    block.difficulty,
    msg.sender
))) % 100;
```

The miner can manipulate `block.timestamp`. `block.difficulty` is public. `msg.sender` is the caller. All inputs are knowable. The output is deterministic.

### The Fix

Chainlink VRF (Verifiable Random Function):

```solidity
function requestRandomNumber() external returns (uint256 requestId) {
    return COORDINATOR.requestRandomWords(keyHash, subId, 3, 100000, 1);
}

function fulfillRandomWords(uint256 requestId, uint256[] calldata randomWords) internal override {
    uint256 random = randomWords[0] % 100;
    // Randomness verified by Chainlink oracle network
}
```

---

## Pattern #54: Bot Farming

**Severity**: HIGH

One bot operator with 1,000 wallets > 1,000 human players with one wallet each. The bot captures the rewards. Human players cannot compete. They quit. The game dies.

### The Fix

Proof-of-humanity, captcha integration, or stake-to-play mechanisms. None are perfect. All raise the cost of botting.

---

*Next: Chapter 21 — AI Agent Security*
