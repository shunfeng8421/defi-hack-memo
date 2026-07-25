# Chapter 20: GameFi Economic Attacks

*"When money meets games, players optimize for profit. When profit extraction exceeds value creation, the game dies."*

---

## The Axie Infinity Death Spiral

At its peak in November 2021, Axie Infinity was generating over $200 million in monthly revenue. Players in the Philippines were earning more than the national minimum wage by breeding, battling, and selling digital creatures called Axies. The game's token, Smooth Love Potion (SLP), was earned by playing and spent on breeding. The game's governance token, AXS, had a market cap exceeding $9 billion.

The economics appeared sustainable: new players bought Axies from existing players, creating a constant inflow of capital. SLP was burned when players bred new Axies, creating deflationary pressure. The "play-to-earn" model was hailed as the future of work.

Then the music stopped.

New player growth slowed. Existing players continued earning SLP. Supply grew faster than demand. SLP's price fell. Players earned less. They played more to compensate—generating even more SLP. The price fell further. The death spiral accelerated.

By mid-2022, SLP had lost 99% of its value. Players who had invested thousands of dollars in Axie teams found their assets worth less than the electricity cost to play. The Philippine "play-to-earn" economy collapsed. Axie Infinity was not hacked. It was not exploited. It was destroyed by the mathematics of an inflationary token with insufficient demand.

The lesson: **GameFi is not gaming with DeFi elements. It is DeFi with a gaming interface. The economic model matters more than the gameplay. If the tokenomics break, no amount of fun gameplay can save it.**

---

## The GameFi Attack Surface

GameFi combines two disciplines with fundamentally different incentive structures:

| | Gaming | DeFi |
|------|------|------|
| Goal | Fun | Profit |
| Player motivation | Mastery, competition, story | Yield, arbitrage, speculation |
| Failure mode | Players quit (boredom) | Protocol collapses (insolvency) |
| Security model | Anti-cheat (client-side) | Smart contract audit (server-side) |

The collision point is the token. A game token that is both a "fun reward" and a "financial asset" must satisfy both gaming economics and DeFi economics. It almost never does.

---

## Pattern #62: Tokenomic Death Spiral

**Severity**: CRITICAL
**Real case**: Axie Infinity, STEPN, virtually every GameFi project

### The Vulnerability

A token is earned by playing and has no effective sink mechanism. Supply grows continuously. Demand depends on new player growth. When growth stops, supply continues → price drops → players earn less per hour → players quit → demand drops further → faster death spiral.

```solidity
// ❌ VULNERABLE: Infinite mint, no effective burn
function claimReward() external {
    uint256 reward = calculateReward(msg.sender);  // Based on play time
    rewardToken.mint(msg.sender, reward);
    // No burn mechanism. Every reward increases total supply forever.
}
```

### The Diagnosis

Ask: what happens to the token price if no new players join for one month?

- If the answer is "the price keeps falling until players quit," the tokenomics are a death spiral.
- If the answer is "the price stabilizes because tokens are burned by existing players," the tokenomics have a floor.

### The Fix

Token sinks that scale with supply:

```solidity
function breedAxie() external {
    uint256 slpCost = calculateBreedingCost(totalSupply);  // Higher supply = higher cost
    slpToken.burn(msg.sender, slpCost);  // Permanent removal
    _mintAxie(msg.sender);
}
```

The cost of core game actions must increase as the token supply increases. This creates natural equilibrium: more tokens in circulation → breeding costs more → more tokens burned → supply stabilizes.

---

## Pattern #63: On-Chain RNG Manipulation

**Severity**: HIGH

### The Vulnerability

Games use random number generation for loot drops, card draws, critical hits, and other probabilistic outcomes. On-chain RNG is deterministic—every input is public and every output is predictable.

```solidity
// ❌ VULNERABLE: Deterministic, miner-manipulable RNG
uint256 random = uint256(keccak256(abi.encodePacked(
    block.timestamp,   // Miner controls within a few seconds
    block.prevrandao,  // Known before block is mined
    msg.sender         // Attacker controls
))) % 100;
```

### The Attack

1. Attacker simulates the RNG calculation off-chain
2. Attacker determines: "if block.timestamp is 1648000000, I get the legendary drop"
3. Attacker submits the transaction with precise timing
4. If the block is mined within the favorable timestamp window, the attacker wins
5. If not, the transaction reverts (attacker sets tight slippage), costing only gas

### The Fix

Chainlink VRF (Verifiable Random Function):

```solidity
function requestRandomNumber() external returns (uint256 requestId) {
    return COORDINATOR.requestRandomWords(keyHash, subId, 3, 100000, 1);
}

function fulfillRandomWords(uint256, uint256[] calldata randomWords) internal override {
    uint256 random = randomWords[0] % 100;
    // Randomness verified by Chainlink oracle network
    // Attacker cannot predict or manipulate
}
```

---

## Pattern #64: Bot Farming

**Severity**: HIGH

### The Vulnerability

One bot operator with 1,000 wallets earns more than 1,000 human players with one wallet each. The bot can play 24/7, never gets tired, and executes strategies with sub-second precision.

### The Attack

1. Bot operator programs a script that plays the game perfectly
2. 1,000 wallets execute the script simultaneously
3. Daily rewards are captured by the bot before human players can claim them
4. Human players cannot compete → they quit → the game becomes bot-vs-bot → the token has no real demand

### The Fix

Sybil resistance mechanisms:
- **Proof-of-Humanity**: Biometric verification that each account is a unique human
- **Stake-to-Play**: Players must lock tokens to participate, making bots expensive
- **Captcha Challenges**: Periodic human verification during gameplay
- **Time-Based Limits**: Daily play caps that make 1,000 accounts no more profitable than 1

None are perfect. All raise the cost of botting. The goal is to make botting economically irrational, not impossible.

---

## Pattern #65: NFT Duplication via Reentrancy

**Severity**: HIGH

### The Vulnerability

Game items are ERC-721 or ERC-1155 tokens. A minting function that mints before updating state—combined with an `onERC721Received` callback—enables reentrancy duplication:

```solidity
function claimReward() external {
    uint256 tokenId = _mint(msg.sender);  // Mints NFT, triggers onERC721Received
    claimed[msg.sender] = true;           // State update AFTER mint
    // If onERC721Received re-enters claimReward(), claimed is still false
}
```

### The Real Case

CryptoKitties—the first major NFT game—had early breeding contracts vulnerable to this exact pattern. Players could breed the same pair of cats multiple times by exploiting the callback before the breeding cooldown was recorded.

### The Fix

CEI (Pattern #2) applies to GameFi too. Update state before minting:

```solidity
function claimReward() external {
    require(!claimed[msg.sender], "Already claimed");
    claimed[msg.sender] = true;  // State update BEFORE external call
    _mint(msg.sender);           // Mint with callback LAST
}
```

---

## The GameFi Economics Checklist

1. **Token supply has a sink that scales with supply growth.** Burn mechanisms must proportionally increase.
2. **RNG is verifiably random and not manipulable by miners or players.** Use Chainlink VRF.
3. **Botting is economically unattractive.** Sybil resistance, stake-to-play, time-based limits.
4. **NFT minting follows CEI and uses ReentrancyGuard.** Game items are financial assets.
5. **The game survives if new player growth stops.** Model this scenario explicitly.

---

## Connection to Other Chapters

- **Ch4 (Flash Loans)**: Axie's death spiral was not caused by a flash loan. But a flash-loaned capital injection could temporarily appear as "new player growth," masking the spiral until the loan is repaid.
- **Ch9 (Reentrancy)**: NFT duplication in GameFi is reentrancy (Pattern #21) applied to game items. The fix is identical: CEI.
- **Ch14 (MEV)**: Bot farming is MEV applied to game mechanics. The bot extracts value from the game's incentive structure just as a MEV searcher extracts value from transaction ordering.

---

*Next: Chapter 21 — AI Agent Security*
