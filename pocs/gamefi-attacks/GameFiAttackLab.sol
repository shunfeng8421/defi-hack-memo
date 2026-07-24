// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title GameFi Attack Lab — 6 Blockchain Gaming Vulnerability Patterns
/// @notice When money meets games, the incentives break everything
/// @author Shiqiang Chen · July 2026

// ============================================================
// #1: Random Number Manipulation
// ============================================================
contract Attack1_GameFi_Randomness {
    // Problem: Blockchain is deterministic → true randomness is impossible on-chain
    // Game: Loot box → random number → legendary item drops
    //
    // BAD RNG sources (all exploitable):
    // 1. block.timestamp → miner controls it
    // 2. blockhash(block.number) → same for all txns in block
    // 3. block.difficulty → predictable
    // 4. private on-chain seed → can be read from storage
    //
    // Attack: Calculate the same RNG that the contract uses
    // → know exactly when to mint for legendary drop
    //
    // Fix: Chainlink VRF (verifiable random function) — but costs LINK gas
    // Better: Commit-reveal with user + protocol random seeds
}

// ============================================================
// #2: Tokenomics / Reward Loop
// ============================================================
contract Attack2_GameFi_RewardLoop {
    // Problem: Game rewards tokens → players farm → sell → price drops → game dies
    //
    // Classic death spiral:
    // 1. Game launches, token = $1
    // 2. Players farm 1000 tokens/day → sell → price drops 20%
    // 3. Token = $0.80 → players farm MORE to compensate → sell MORE
    // 4. Token = $0.10 → game economy dead
    //
    // Real: Axie Infinity, STEPN — both hit this wall
    //
    // Attack: Not a hack — just math. Infinite supply > finite demand = 0
    // Fix: Sink mechanisms (item burning, stake-to-play, time-locked rewards)
}

// ============================================================
// #3: NFT Duplication / Metadata Exploit
// ============================================================
contract Attack3_GameFi_NFTDuplication {
    // Problem: Game assets are ERC-721 tokens. Duplication = inflation.
    //
    // Attack vectors:
    // 1. Reentrancy on mint(): Call mint() → callback → mint() again
    // 2. Metadata poisoning: Change tokenURI to point to fake metadata server
    // 3. ERC-1155 batch mint overflow: uint256 overflow → 0-cost mint infinite
    //
    // Real: CryptoKitties — early versions had reentrancy breeding bugs
    //
    // Fix: ReentrancyGuard on all mint/breed; immutable metadata; SafeMath
}

// ============================================================
// #4: Botting / Automated Farming
// ============================================================
contract Attack4_GameFi_Botting {
    // Problem: Scriptable, permissionless blockchain = bot paradise
    //
    // One bot operator > 1000 human players:
    // 1. Deploy 1000 wallets programmatically
    // 2. Each wallet simulates a "human player"
    // 3. Capture 99% of daily rewards
    // 4. Human players can't compete → quit → game dies
    //
    // Detection: Identical play patterns; bot detection via ML
    // But: Sophisticated bots randomize behavior → undetectable
    //
    // Fix: Sybil resistance (Proof-of-Humanity, Gitcoin Passport, CAPTCHA)
    // But: Every sybil resistance can be farmed at scale
}

// ============================================================
// #5: Front-running Game Actions
// ============================================================
contract Attack5_GameFi_Frontrunning {
    // Problem: Game actions are on-chain transactions → MEV possible
    //
    // Example: Racing game — winner gets $1000
    // 1. Player submits winning move
    // 2. MEV bot sees it in mempool
    // 3. Bot copies the winning move with higher gas → wins instead
    //
    // Fix: Commit-reveal for competitive actions
    // 1. Player commits hash(move + secret)
    // 2. All moves committed → reveal phase → compare moves → declare winner
    //
    // But: Adds latency → bad UX for gaming
}

// ============================================================
// #6: Governance Capture via Game Tokens
// ============================================================
contract Attack6_GameFi_Governance {
    // Problem: Game governance token = play-to-earn reward
    // Result: Most active players accumulate governance power
    // They're economically incentivized to vote for MAXIMUM inflation
    //
    // Attack: Voting block of farmers votes to:
    // 1. Increase daily rewards
    // 2. Reduce token burn rate
    // 3. Remove play-to-earn caps
    // → Hyperinflation → token to 0 → everyone loses
    //
    // Fix: Time-locked governance; weighted voting (staked longer = more power)
    // Critical insight: Gamers optimize for FUN → DeFi optimizes for MONEY
    // GameFi = irreconcilable tension
}

/// @title GameFi Summary
/// @dev The fundamental tension: Game incentives ≠ Economic incentives
/// Every GameFi failure comes from optimizing one at the expense of the other
