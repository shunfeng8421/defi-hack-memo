# Chapter 4: Flash Loan Attacks

*"Before flash loans, an attacker needed money. After flash loans, an attacker needed gas."*

---

## The Attack That Changed Everything

On May 20, 2021, at 15:29 UTC, a developer named "Frank" submitted a transaction to the PancakeBunny protocol on Binance Smart Chain. The transaction borrowed 697,000 BNB — worth approximately $300 million — from Aave's lending pool. It cost Frank 0.04 BNB in gas fees.

Frank was not a whale. He did not have $300 million. The loan was a flash loan: borrow any amount, use it within the same transaction, repay it within the same transaction. If you fail to repay, the entire transaction reverts as if nothing happened. The only cost is gas.

Within the same transaction, Frank used the borrowed BNB to execute a series of swaps across PancakeBunny's liquidity pools. These swaps manipulated the spot price that PancakeBunny used to calculate rewards. At the manipulated price, the protocol minted 697,000 newly-created BUNNY tokens and sent them to Frank as his "yield farming reward." Frank immediately sold the BUNNY tokens, repaid the flash loan, and pocketed the difference.

Total profit: approximately $120 million. Total time elapsed: less than one block. Total capital required: 0.04 BNB.

The PancakeBunny exploit was not the first flash loan attack. It was not the largest. But it was the one that made the entire DeFi industry understand something fundamental: **flash loans have made every attack vector that requires capital into an attack vector that requires nothing.**

---

## What Is a Flash Loan?

A flash loan is an uncollateralized loan that must be borrowed and repaid within a single Ethereum transaction. If the borrower fails to repay the full amount plus any fee, the entire transaction is reverted by the lending contract. From the protocol's perspective, the loan never happened.

Flash loans were pioneered by Aave in 2020. The mechanism is simple:

```solidity
function flashLoan(
    address receiver,
    uint256 amount
) external {
    uint256 balanceBefore = token.balanceOf(address(this));
    token.transfer(receiver, amount);
    
    receiver.onFlashLoan(msg.sender, amount, "");  // User's callback
    
    uint256 balanceAfter = token.balanceOf(address(this));
    require(balanceAfter >= balanceBefore, "Not repaid");
}
```

The `receiver.onFlashLoan()` callback is where the user does whatever they want with the borrowed funds. When the callback returns, the contract verifies repayment. If repayment failed, the entire transaction reverts — including everything the user did with the borrowed funds.

This is why flash loans have zero credit risk for the lender. The atomicity guarantee of the Ethereum Virtual Machine ensures that either the loan is repaid, or nothing happened. There is no intermediate state where the borrower has the funds and has not repaid.

---

## Why Flash Loans Are a Security Primitive

Before flash loans, attacking a DeFi protocol required capital. To manipulate a price oracle, you needed funds to execute swaps. To exploit a governance mechanism, you needed voting tokens. To drain a vault, you needed enough to make the exploit worthwhile after accounting for gas costs.

Flash loans eliminated this constraint. The attacker's cost is now exactly the gas fee of the transaction — typically a few dollars. This fundamental change means:

1. **Every vulnerability that requires capital is now accessible to anyone.** The total addressable attacker population went from "people with money" to "people with a computer."

2. **Minimum profitable exploit size collapsed.** Previously, an exploit needed to extract enough value to cover the attacker's capital deployment cost. With flash loans, the only cost is gas. A $1,000 exploit is now profitable if gas costs $5.

3. **Composability becomes attack surface.** Every protocol that a flash-loaned asset can interact with within a single transaction is a potential target. The PancakeBunny attacker didn't attack Aave — they used Aave as a weapon.

---

## Pattern #1: Flash Loan + Spot Price Oracle

**Severity**: CRITICAL
**Real cases**: PancakeBunny $120M, CREAM $130M, Harvest Finance $34M, bEarn $11M

### The Vulnerability

A protocol reads the price of an asset from a decentralized exchange's current reserves. These reserves change whenever anyone swaps tokens in the pool.

```solidity
// ❌ VULNERABLE: Spot price from Uniswap V2 getReserves()
function getAssetPrice() public view returns (uint256) {
    (uint256 reserve0, uint256 reserve1, ) = pair.getReserves();
    return reserve0 * 1e18 / reserve1;
}
```

This function returns a price that is valid for exactly one instant: the moment it was called. The next swap in the pool will change the reserves. The function has no memory of what the price was one second ago, and no protection against rapid manipulation.

### The Attack

1. **Borrow**: Flash loan a massive amount of asset A
2. **Manipulate**: Swap asset A into the pool → reserves change → spot price drops
3. **Exploit**: Call the vulnerable protocol → it reads the manipulated price → overvalues the attacker's position
4. **Extract**: Withdraw at the inflated valuation
5. **Repay**: Repay the flash loan
6. **Profit**: The difference between the true value and the manipulated valuation

The entire sequence executes atomically. No human can intervene between steps. No monitoring system can react in time. By the time the transaction is confirmed, the money is gone.

### Why It Keeps Happening

The spot price oracle pattern persists because it is seductively simple. `getReserves()` is a one-line function call. TWAP requires deploying a separate oracle contract and waiting for price observations to accumulate. Chainlink requires selecting a feed, handling staleness, and adding fallback logic.

Developers optimize for implementation time, not attack resilience. The one-line solution ships faster. The attacker arrives later.

### The Fix

```solidity
// ✅ SAFE: Uniswap V2 TWAP oracle (consult)
function getAssetPrice() public view returns (uint256) {
    return pair.consult(token, amount);
    // consult(): queries the cumulative price history,
    // returns time-weighted average, not instantaneous spot
}
```

Or use Chainlink with staleness checks:

```solidity
// ✅ SAFE: Chainlink with freshness verification
function getAssetPrice() public view returns (uint256) {
    (, int256 price, , uint256 updatedAt, ) = feed.latestRoundData();
    require(block.timestamp - updatedAt < 1 hours, "Price stale");
    return uint256(price);
}
```

### Detection with the Scanner

The 58-pattern scanner detects this pattern with two regex rules:

```python
pattern = {
    "regex": [r'getReserves\(\)', r'\.balance\b'],
    "keyword": ["price", "oracle", "value", "!TWAP", "!cumulative", "!Chainlink", "!consult"],
    "description": "Instant spot price used as oracle input"
}
```

The negated keywords are what make this detection useful. A file that uses `getReserves()` but also imports `TWAP` or references `cumulative` is likely using the oracle correctly. A file that uses `getReserves()` with none of those safety checks is suspect.

---

## Pattern #2: Flash Loan + Governance Attack

**Severity**: CRITICAL
**Real case**: Beanstalk $182M (April 2022)

### The Vulnerability

Governance tokens can be flash-loaned just like any other token. If a protocol's governance uses token-weighted voting, and the tokens are available on any lending market, an attacker can borrow enough voting power to pass any proposal.

### The Attack

1. **Borrow**: Flash loan a supermajority of the governance token from a lending pool
2. **Vote**: Submit and pass a malicious proposal — typically an "emergency upgrade" that transfers all protocol funds to the attacker
3. **Execute**: The proposal's timelock expires (if any), or the attacker calls the governance execution function directly
4. **Repay**: Repay the flash loan
5. **Result**: The attacker now controls the protocol's treasury

Beanstalk lost $182 million this way. The attacker borrowed 350 million BEAN tokens — approximately 75% of the total supply — from Aave, used them to vote through an emergency governance proposal, and drained the protocol's treasury. The entire attack took less than 30 seconds.

### Why Governance Isn't Safe

The defense against governance attacks is the assumption that acquiring enough voting power is expensive. If you need to buy 51% of the tokens to pass a proposal, it costs at least 51% of the market cap. This cost — the "cost of corruption" — is what makes governance secure.

Flash loans eliminate the cost of corruption. The attacker doesn't need to buy the tokens. They borrow them, vote, and return them.

### The Fix

Governance must not use instantaneous token balances for voting power:

```solidity
// ❌ VULNERABLE: Current balance determines voting power
function getVotes(address account) public view returns (uint256) {
    return token.balanceOf(account);
}

// ✅ SAFE: Voting power snapshotted at proposal creation
function getVotes(address account) public view returns (uint256) {
    return votes[account][proposalSnapshot[proposalId]];
}
```

Snapshots ensure that the voting power used for a proposal is recorded when the proposal is created, not when it is voted on. An attacker who flash-loans tokens after the proposal exists cannot use them to vote.

Many protocols also implement a minimum holding period — tokens must be held for at least N blocks before they confer voting power. This prevents flash-loan voting even on proposals where the snapshot mechanism is not used.

---

## Pattern #3: Flash Loan + Vault Inflation

**Severity**: HIGH
**Real cases**: Multiple ERC-4626 vault exploits

### The Vulnerability

ERC-4626 vaults use a share-based accounting model. When you deposit tokens, you receive shares proportional to your deposit relative to the total value locked. The share price is calculated as:

```
share price = total vault value / total shares
```

The first depositor can manipulate this calculation.

### The Attack

1. **Borrow**: Flash loan a large amount of the vault's underlying token
2. **Deposit**: Deposit 1 wei into the empty vault → receive 1 share
3. **Donate**: Transfer a massive amount of tokens directly to the vault (bypassing the deposit function, so no shares are minted)
4. **Inflate**: Share price = (1 wei + massive donation) / 1 share = astronomical
5. **Victim deposits**: The next depositor's tokens are divided by the astronomical share price → they receive 0 shares due to rounding
6. **Profit**: The attacker's 1 share now represents the entire vault value
7. **Repay**: Repay the flash loan (the attack profit comes from the victim's deposit, not the borrowed funds)

This attack works because the vault's accounting system treats donations as legitimate deposits. The share price inflation is genuine — from the contract's perspective, someone did add value.

### The Fix

The standard defense is a virtual offset — the vault maintains a minimum total supply and a minimum total assets that prevent price inflation from a single depositor:

```solidity
// ✅ SAFE: Virtual offset prevents inflation
uint256 constant VIRTUAL_SHARES = 10 ** 6;
uint256 constant VIRTUAL_ASSETS = 1;

function convertToShares(uint256 assets) public view returns (uint256) {
    return assets.mulDiv(
        totalSupply + VIRTUAL_SHARES,
        totalAssets + VIRTUAL_ASSETS,
        Math.Rounding.Down
    );
}
```

The virtual shares and assets act as an initial deposit that no one owns. The first real depositor cannot inflate the share price because the total supply and total assets never start from zero.

---

## The Flash Loan Detector

The 58-pattern scanner dedicates an entire section to flash loan attack detection: patterns 1-8. These eight patterns cover:

| Pattern | Name | Severity |
|:--:|------|:--:|
| 1 | Flash Loan + Spot Price | CRITICAL |
| 2 | CEI Violation (Reentrancy) | CRITICAL |
| 3 | Flash Loan + Reentrancy Combo | CRITICAL |
| 4 | TWAP Multi-Block Manipulation | HIGH |
| 5 | ERC-4626 Vault Inflation | HIGH |
| 6 | Flash Loan Governance Attack | CRITICAL |
| 7 | AMM Reserve Manipulation | HIGH |
| 8 | Rate/Incentive Manipulation | MEDIUM |

Each pattern has specific regex rules, keyword matching, and fix recommendations. The scanner detects the *pattern* — human judgment determines whether it's a real vulnerability or a false positive.

---

## Why Flash Loans Are Here to Stay

Every attempt to ban or restrict flash loans has failed. The mechanism is too useful. Flash loans enable arbitrage, liquidation, portfolio rebalancing, and countless legitimate financial operations that benefit the ecosystem.

The security researcher's job is not to eliminate flash loans. It is to ensure that protocols are designed with the knowledge that **any amount of any token is available to anyone in a single transaction.** If your protocol breaks under this assumption, it will break.

---

*Next: Chapter 5 — Oracle Manipulation*
