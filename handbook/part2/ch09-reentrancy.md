# Chapter 9: Reentrancy & Callbacks

*"The most famous bug in blockchain history is 20 lines of code that anyone can write and nobody can fix after deployment."*

---

## The DAO: June 17, 2016

At 3:34 AM UTC, an unknown attacker began draining ETH from The DAO — a decentralized venture fund holding 12.7 million ETH, approximately $150 million at the time. Over the next several hours, 3.6 million ETH flowed into a child DAO controlled by the attacker.

The Ethereum community watched in real time as the largest crowdfunded project in history was systematically emptied. There was nothing anyone could do. The code was immutable. The attack was a single function, called recursively, exploiting a one-line ordering mistake.

The DAO hack was not the first reentrancy attack — the concept predates Ethereum. But it was the attack that taught an entire generation of developers a lesson they would never forget: **never make an external call before updating your state.**

The Ethereum community's response was the most controversial decision in blockchain history: a hard fork to reverse the theft. The chain that refused to fork — where the attacker kept the money — became Ethereum Classic. The chain that forked became the Ethereum we know today.

---

## What Is Reentrancy?

Reentrancy occurs when a contract makes an external call to another contract, and that contract calls back into the original contract before the original contract has finished updating its state.

The simplest example:

```solidity
contract VulnerableVault {
    mapping(address => uint256) public balances;
    
    function withdraw() external {
        uint256 amount = balances[msg.sender];
        
        // ❌ External call BEFORE state update
        (bool success,) = msg.sender.call{value: amount}("");
        require(success);
        
        // State updated AFTER external call — too late!
        balances[msg.sender] = 0;
    }
}
```

The attacker's contract:

```solidity
contract Attacker {
    VulnerableVault public vault;
    
    function attack() external payable {
        vault.deposit{value: 1 ether}();
        vault.withdraw();  // Triggers reentrancy
    }
    
    receive() external payable {
        if (address(vault).balance >= 1 ether) {
            vault.withdraw();  // Re-enter before balance is set to 0!
        }
    }
}
```

Execution trace:

1. `attacker.attack()` → deposits 1 ETH → calls `vault.withdraw()`
2. `vault.withdraw()` reads `balances[attacker] = 1 ETH` → sends 1 ETH to attacker
3. `attacker.receive()` fires → checks vault still has funds → calls `vault.withdraw()` AGAIN
4. `vault.withdraw()` reads `balances[attacker] = 1 ETH` (still hasn't been updated!) → sends another 1 ETH
5. Repeat until the vault is empty
6. Finally, all recursive calls unwind, `balances[attacker] = 0` is set, but the vault is already drained

---

## The CEI Pattern: Checks-Effects-Interactions

The universal defense against reentrancy:

```solidity
function withdraw() external {
    uint256 amount = balances[msg.sender];
    
    // 1. CHECKS: Verify conditions
    require(amount > 0, "No balance");
    
    // 2. EFFECTS: Update state BEFORE external calls
    balances[msg.sender] = 0;
    
    // 3. INTERACTIONS: Make external calls LAST
    (bool success,) = msg.sender.call{value: amount}("");
    require(success);
}
```

If the attacker's `receive()` re-enters `withdraw()` after step 2, `balances[msg.sender]` is already 0. The re-entrant call hits the `require(amount > 0)` check and reverts. The attack fails.

---

## Modern Reentrancy: ERC-777 Callbacks

The classic reentrancy pattern is well-known and well-defended. Modern reentrancy attacks exploit callbacks that developers don't know exist.

ERC-777 tokens call a `tokensReceived()` callback on the recipient during every transfer. If your protocol transfers ERC-777 tokens and then updates state, the callback can re-enter your protocol.

```solidity
// ❌ VULNERABLE: ERC-777 transfer triggers callback
function deposit(uint256 amount) external {
    token.transferFrom(msg.sender, address(this), amount);
    // token.transferFrom() → tokensReceived() callback on THIS contract
    // Callback can re-enter deposit() before balance is updated!
    balances[msg.sender] += amount;
}
```

The attack works exactly like the classic pattern, but the entry point is hidden inside a token standard that looks innocent.

### The Fix

```solidity
function deposit(uint256 amount) external {
    uint256 before = token.balanceOf(address(this));
    token.transferFrom(msg.sender, address(this), amount);  // May callback
    uint256 afterBalance = token.balanceOf(address(this));
    balances[msg.sender] += (afterBalance - before);  // Uses actual received
}
```

By using balance deltas instead of the stated amount, the attack is neutralized. Even if the callback re-enters, the balance difference reflects reality.

---

## Cross-Function Reentrancy

A contract may have `withdrawA()` and `withdrawB()` that both protect against reentrancy individually, but share state that makes them vulnerable when called together:

```solidity
function withdrawA() external {
    require(balanceA[msg.sender] > 0);
    balanceA[msg.sender] = 0;
    msg.sender.call{value: amount}("");  // Re-enters
}

function withdrawB() external {
    require(balanceB[msg.sender] > 0);
    balanceB[msg.sender] = 0;
    msg.sender.call{value: amount}("");  // Called from withdrawA's re-entry
}
```

Each function individually follows CEI. But the attacker calls `withdrawA()` → `receive()` → `withdrawB()` → drains both balances. The `balances[msg.sender]` for `withdrawA` was set to 0, but `withdrawB` reads a different mapping.

### The Fix

Use a single reentrancy guard for the entire contract:

```solidity
modifier nonReentrant() {
    require(!locked, "Reentrant call");
    locked = true;
    _;
    locked = false;
}
```

OpenZeppelin's `ReentrancyGuard` provides this out of the box.

---

## Read-Only Reentrancy

Not all reentrancy extracts funds. Some reentrancies exploit the fact that the contract's state is temporarily inconsistent during the external call.

```solidity
function deposit() external payable {
    totalDeposits += msg.value;  
    msg.sender.call("");          // External call with inconsistent state
    emit Deposited(msg.sender, msg.value);  // Event emitted after
}
```

During the external call, `totalDeposits` has been updated but the `Deposited` event has not been emitted. An attacker monitoring events might miss the deposit. A contract reading `totalDeposits` during this window sees an intermediate state.

This class is harder to exploit but has been used in sophisticated MEV and oracle manipulation attacks.

---

## The Reentrancy Checklist

1. **Does every external call happen AFTER all state updates?** If not, it must.
2. **Does the contract interact with ERC-777, ERC-1155, or ERC-721 tokens?** These all have callbacks during transfer.
3. **Does the contract have multiple functions that share state?** Cross-function reentrancy can bypass single-function CEI.
4. **Is `ReentrancyGuard` applied to every external function?** Not just the ones you think are vulnerable.

---

*Next: Chapter 10 — Initialization & Upgrade Attacks*
