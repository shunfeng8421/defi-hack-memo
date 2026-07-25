# Chapter 14: MEV & Front-Running

*"Every pending transaction in the mempool is an opportunity. The question is: whose opportunity?"*

---

## The makina Incident: January 2026

In January 2026, a MEV searcher known as "makina" deployed a sophisticated bot designed to capture arbitrage opportunities on Ethereum. The bot monitored the mempool for profitable transactions—large swaps that created price discrepancies between decentralized exchanges—and submitted counter-transactions that captured the profit before the original trader.

makina's bot was highly successful. Over several months, it extracted millions of dollars in MEV profit. Its strategy was well-known, its transaction patterns recognizable. Other MEV searchers learned to avoid competing with makina's bot—it had more capital, faster execution, and better validator connections.

Then someone turned the tables.

An attacker studied makina's bot. They reverse-engineered its strategy, identified its transaction submission patterns, and noticed a critical detail: makina's bot used flash loans to amplify its positions, but did not validate the loan's callback conditions. The attacker crafted a transaction that appeared to be a profitable arbitrage opportunity, baiting makina's bot into taking a flash loan to capture it. When the bot's callback executed, the attacker's contract drained the bot's funds.

The bot that had extracted millions from other traders was itself extracted for $5.1 million.

The makina incident is the defining case study of MEV security because it demonstrates the meta-game: **MEV is not just about extracting value from users. It is about extracting value from other MEV extractors.** The food chain of the mempool has no top predator. Everyone is someone else's prey.

---

## What Is MEV?

Maximal Extractable Value—originally "Miner Extractable Value"—is the profit that can be extracted from a blockchain by including, excluding, or reordering transactions within a block.

In traditional finance, transaction ordering is handled by the exchange. The exchange receives all orders, sorts them by price-time priority, and executes them atomically. No participant can see another participant's order before it executes.

In DeFi, transaction ordering is handled by validators. Every pending transaction sits in a public mempool, visible to anyone running a node, before it is included in a block. During this window—typically a few seconds on Ethereum, longer on congested networks—anyone can:

1. **See** the pending transaction and understand its intent
2. **Copy** it with higher gas fees to execute first
3. **Insert** transactions before and after to extract value
4. **Suppress** it by outbidding for block space

This visibility window is the source of all MEV. If mempools were private—if nobody could see pending transactions—MEV would not exist. But mempools are public by design, and that design creates a multi-billion-dollar secondary market in transaction ordering.

---

## Pattern #34: Classic Sandwich Attack

**Severity**: HIGH

### The Attack

A user submits a transaction to swap 100 ETH for USDC on Uniswap. The transaction sits in the mempool. A MEV searcher sees it and submits two transactions:

1. **Buy** the same token BEFORE the user's trade (raises the price)
2. **Sell** the token AFTER the user's trade (lowers the price back)

The user's trade executes at an artificially inflated price—they receive fewer USDC than expected. The MEV searcher profits from the difference between the pre-trade price and the post-trade price. The user's slippage tolerance determines the searcher's profit.

```solidity
// The sandwich attack, simplified
// 1. Searcher front-runs: buyToken() at price P
// 2. Victim trades at inflated price P' > P
// 3. Searcher back-runs: sellToken() at price P'' ≈ P
// Profit = (P' - P) * victimAmount
```

### The Fix

The user's defense is the **slippage tolerance**. If the user sets `maxSlippage = 0.5%`, the transaction reverts if the price moves more than 0.5% from the quoted price. The sandwich fails.

But slippage tolerance is a trade-off. A tight tolerance (0.1%) provides strong MEV protection but increases the chance of the transaction failing due to normal market movement. A loose tolerance (5%) ensures execution but leaves the user vulnerable to sandwiches.

---

## Pattern #35: Just-In-Time Liquidity

**Severity**: HIGH

### The Attack

A large swap is visible in the mempool. A liquidity provider sees the swap and:

1. **Adds** concentrated liquidity to the exact price range the swap will traverse
2. The swap executes through the newly added liquidity
3. The LP **removes** the liquidity immediately after the swap processes

The LP captures the swap fees without bearing any inventory risk. They were only providing liquidity for the duration of one transaction.

This attack is unique to Uniswap V3's concentrated liquidity model. In V2, liquidity was uniform across all price ranges—adding liquidity took time to deploy capital across the entire curve. In V3, a single tick-wide position can capture fees from a single swap.

### The Fix

Minimum liquidity duration:

```solidity
mapping(address => uint256) public liquidityAddedAt;

function addLiquidity(...) external {
    liquidityAddedAt[msg.sender] = block.timestamp;
    // ... add liquidity
}

function removeLiquidity(...) external {
    require(
        block.timestamp >= liquidityAddedAt[msg.sender] + 10 minutes,
        "Minimum duration not met"
    );
    // ... remove liquidity
}
```

---

## Pattern #36: Multi-Block MEV

**Severity**: MEDIUM

### The Attack

Single-block MEV protection (such as Uniswap V2's TWAP oracle with a 30-minute window) assumes that an attacker cannot control consecutive blocks. This assumption is weak.

An attacker who controls multiple consecutive blocks—through validator collusion, MEV-Boost relay manipulation, or simply by being a validator—can manipulate the price across the entire window:

1. Block N: Manipulate price up significantly
2. Block N+1: Maintain manipulated price
3. Block N+2: Protocol reads TWAP → average of manipulated prices → accepts fake value

The attack is expensive—it requires validator-level access—but for high-value targets (bridges, lending protocols with large TVL), the cost may be justified.

### The Fix

Longer TWAP windows. A 30-minute window on Ethereum (approximately 150 blocks) makes multi-block MEV economically infeasible because controlling 150 consecutive blocks is exponentially more expensive than controlling 3.

---

## Pattern #37: MEV Bot Replay / Counter-Attack

**Severity**: HIGH
**Real case**: makina $5.1M

### The Attack

MEV bots are smart contracts that make financial decisions autonomously. If the bot's strategy can be predicted, an attacker can construct transactions that exploit the bot's own logic:

1. **Study** the bot's transaction history on Etherscan
2. **Reverse-engineer** the bot's strategy from its call patterns
3. **Construct** a decoy transaction that triggers the bot's strategy
4. **Exploit** the bot's callback or flash loan repayment condition

makina's bot was exploited because it used flash loans without validating the callback's conditions. The attacker's transaction triggered the bot's flash loan, and the callback was designed to drain the bot rather than repay the loan.

### The Fix

MEV bots must apply the same security principles as any other DeFi protocol:

```solidity
function onFlashLoan(address initiator, address token, uint256 amount, uint256 fee, bytes calldata data) external returns (bytes32) {
    require(msg.sender == address(lendingPool), "Invalid caller");
    require(initiator == address(this), "Invalid initiator");
    
    // Validate strategy profitability
    uint256 profit = executeStrategy(token, amount);
    require(profit > fee, "Unprofitable trade");
    
    // Repay loan
    IERC20(token).approve(address(lendingPool), amount + fee);
    return FLASH_LOAN_CALLBACK;
}
```

---

## The MEV Detection Challenge

MEV is harder to detect with static analysis than other vulnerability classes because the vulnerability is rarely in the code. It is in the **interaction** between the code and the mempool environment.

The 58-pattern scanner does not have dedicated MEV patterns because MEV detection requires runtime analysis—simulating transactions against mempool state, not analyzing source code. This is an area where dynamic analysis tools (transaction simulators, mempool monitors) complement static analysis.

---

## The MEV Defense Checklist

1. **Slippage tolerance is set explicitly on every swap.** Never `type(uint256).max`.
2. **Time-sensitive operations use commit-reveal.** Don't expose the action before it's time to act.
3. **TWAP windows are long enough to make multi-block manipulation unprofitable.** 30 minutes minimum.
4. **MEV bot callbacks validate all conditions before executing.** The flash loan callback is the most dangerous function in the bot.
5. **Liquidity removal has a minimum duration.** Just-in-time liquidity is only profitable if the liquidity can be removed immediately.

---

## Connection to Other Chapters

- **Ch4 (Flash Loans)**: MEV bots use flash loans to amplify positions without capital. The makina attack combined flash loan infrastructure with MEV strategy prediction.
- **Ch5 (Oracle Manipulation)**: Multi-block MEV is TWAP oracle manipulation implemented at the validator level. The TWAP defense (long windows) applies to both.
- **Ch8 (Cross-Chain)**: Cross-chain MEV—front-running on one chain to capture value on another—is an emerging attack class that combines cross-chain replay with mempool visibility.

---

*Next: Chapter 15 — Lending Protocol Attacks*
