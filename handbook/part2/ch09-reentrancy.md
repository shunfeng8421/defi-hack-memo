# Chapter 9: Reentrancy & Callbacks

*"The most famous bug in blockchain history was not a cryptographic flaw. It was a function calling a function calling the same function."*

---

## The DAO: June 17, 2016

At 03:34 UTC on June 17, 2016, an anonymous address began interacting with The DAO—a decentralized venture fund that had raised 12.7 million ETH in the largest crowdfunding campaign in history. The interactions were not typical investments. They were withdrawals. Over and over again.

The DAO's smart contract contained a `splitDAO()` function that allowed investors to withdraw their funds and create a child DAO. The function followed this sequence:

1. Check the user's balance
2. Transfer ETH to the user
3. Update the user's balance to zero

Step 2 made an external call to the user's address. If the user was a contract, the contract's `receive()` function was triggered. And inside that `receive()` function, the attacker called `splitDAO()` again.

Step 3—setting the balance to zero—had not executed yet from the first call. The second `splitDAO()` saw the original balance. It transferred ETH again. The attacker's `receive()` called `splitDAO()` again. And again. And again.

By 04:00, 3.6 million ETH—approximately $50 million at the time, $150 million at peak—had been drained into a child DAO controlled by the attacker. The Ethereum community watched in real time as the entire premise of decentralized autonomous organizations was systematically dismantled by a recursive function call.

### The Fork

The Ethereum community faced an impossible choice. Allow the theft to stand, violating the implicit social contract that code is not law when code is clearly broken. Or hard fork the chain to reverse the theft, violating the explicit promise that blockchain transactions are immutable.

After weeks of debate, the community chose to fork. The chain that rolled back the theft became Ethereum. The chain that refused—where the attacker kept the money under the philosophy of "code is law"—became Ethereum Classic.

Both chains exist today. Both philosophies have their adherents. The DAO hack is not just a technical vulnerability. It is the founding trauma of the entire smart contract security discipline. Every Solidity developer who has written `balances[msg.sender] = 0` before `msg.sender.call{value: amount}("")` is following a lesson taught by a recursive function call on June 17, 2016.

---

## The Mechanism of Reentrancy

Reentrancy occurs when a contract makes an external call before updating its own state, and the external contract calls back into the original contract before the state update completes.

The vulnerable pattern:

```solidity
function withdraw() external {
    uint256 amount = balances[msg.sender];     // Step 1: Read state
    
    (bool ok,) = msg.sender.call{value: amount}("");  // Step 2: External call
    require(ok);
    
    balances[msg.sender] = 0;                  // Step 3: Update state
    // ⬆ This hasn't executed when the reentrant call arrives
}
```

The attacker's contract:

```solidity
receive() external payable {
    if (address(vault).balance >= 1 ether) {
        vault.withdraw();  // Re-enter before Step 3 executes
    }
}
```

The execution trace:

```
vault.withdraw()                    [balances = 10 ETH]
  → msg.sender.call{value: 10}     [sends 10 ETH]
    → attacker.receive() fires
      → vault.withdraw()            [balances STILL = 10 ETH]
        → msg.sender.call{value: 10} [sends another 10 ETH]
          → attacker.receive() fires
            → vault.withdraw()       [balances STILL = 10 ETH]
              → ... (continues until vault is empty)
        
        balances[attacker] = 0       [finally executes, but too late]
      balances[attacker] = 0
    balances[attacker] = 0
```

Each recursive call sees the original balance because the update (`balances[msg.sender] = 0`) has not executed for any of the prior calls yet. The stack unwinds from the deepest recursion first, setting the balance to zero for each level—but by then, the funds have already been transferred multiple times.

---

## The CEI Pattern: Checks-Effects-Interactions

The universal defense against reentrancy is the CEI pattern:

```solidity
function withdraw() external {
    uint256 amount = balances[msg.sender];
    
    // 1. CHECKS: Verify all preconditions
    require(amount > 0, "No balance");
    require(amount <= address(this).balance, "Insufficient vault");
    
    // 2. EFFECTS: Update all state BEFORE any external call
    balances[msg.sender] = 0;
    totalDeposits -= amount;
    
    // 3. INTERACTIONS: Make external calls LAST
    (bool ok,) = msg.sender.call{value: amount}("");
    require(ok);
}
```

If the attacker's `receive()` re-enters `withdraw()` after Step 2, `balances[msg.sender]` is already zero. The re-entrant call fails at the `require(amount > 0)` check. The attack is neutralized before it begins.

CEI is not a suggestion. It is a law. Every Solidity developer who violates it—regardless of how "safe" the specific violation appears—is inviting The DAO.

---

## Modern Reentrancy: ERC-777 Callbacks

The classic reentrancy pattern is well-known and well-defended. Modern reentrancy attacks exploit callbacks that developers do not realize exist.

ERC-777 is a token standard that improves on ERC-20 by adding a `tokensReceived()` callback hook. Every transfer of an ERC-777 token calls `tokensReceived()` on the recipient. If the recipient is a smart contract, the contract's code executes during the transfer—before the transfer function has returned.

```solidity
// ❌ VULNERABLE: ERC-777 transfer triggers callback
function deposit(uint256 amount) external {
    erc777Token.send(msg.sender, address(this), amount, "");
    // send() → tokensReceived() callback on THIS contract
    // Callback can re-enter deposit() before balance is updated!
    balances[msg.sender] += amount;
}
```

The attack is identical to the classic pattern, but the entry point is hidden inside a token standard. The developer looked at `deposit()` and saw no external call. They were wrong—the call is inside the token's `send()` function.

ERC-1155 has a similar mechanism. Both standards were designed to improve user experience. Both inadvertently created reentrancy vectors that developers who learned "make external calls last" did not realize they were making.

### The Fix

```solidity
// ✅ SAFE: Balances updated before transfer
function deposit(uint256 amount) external {
    balances[msg.sender] += amount;  // Effect first
    erc777Token.send(msg.sender, address(this), amount, "");  // Interaction last
    // If callback re-enters, balances[msg.sender] already updated
}
```

Or use balance deltas:

```solidity
function deposit(uint256 amount) external {
    uint256 before = erc777Token.balanceOf(address(this));
    erc777Token.send(msg.sender, address(this), amount, "");
    uint256 received = erc777Token.balanceOf(address(this)) - before;
    balances[msg.sender] += received;  // Credits actual received, not stated amount
}
```

---

## Cross-Function Reentrancy

Each function may individually follow CEI, but two functions that share state can create a cross-function reentrancy path.

```solidity
function withdrawETH() external {
    uint256 amount = ethBalances[msg.sender];
    require(amount > 0);
    ethBalances[msg.sender] = 0;
    (bool ok,) = msg.sender.call{value: amount}("");  // External call
    require(ok);
}

function withdrawToken() external {
    uint256 amount = tokenBalances[msg.sender];
    require(amount > 0);
    tokenBalances[msg.sender] = 0;
    token.transfer(msg.sender, amount);  // Another external call
}
```

Individually, both functions are safe. But the attacker can:

1. Call `withdrawETH()` → send ETH → `receive()` fires
2. Inside `receive()`, call `withdrawToken()` → tokens transferred
3. Both balances read the original values before being set to zero

### The Fix

A single reentrancy guard protects the entire contract:

```solidity
modifier nonReentrant() {
    require(!_locked, "Reentrant call");
    _locked = true;
    _;
    _locked = false;
}

function withdrawETH() external nonReentrant { ... }
function withdrawToken() external nonReentrant { ... }
```

OpenZeppelin's `ReentrancyGuard` provides this modifier. Apply it to every external function that modifies state, not just the ones you think are vulnerable.

---

## Read-Only Reentrancy

Not all reentrancy extracts funds directly. Some exploits read temporarily inconsistent state to make decisions that profit the attacker elsewhere.

A contract updates `totalDeposits` before emitting an event, but makes an external call between the two:

```solidity
function deposit() external payable {
    totalDeposits += msg.value;              // State updated
    msg.sender.call("");                     // External call — state inconsistent
    emit Deposited(msg.sender, msg.value);    // Event not yet emitted
}
```

During the external call, `totalDeposits` reflects the new deposit, but the `Deposited` event has not been emitted. A monitoring system that relies on events will miss this deposit. A second contract that reads `totalDeposits` during this window sees a value that does not match the event history.

This is harder to exploit but has been used in sophisticated MEV and cross-contract attack chains where multiple protocols are manipulated simultaneously.

---

## The Reentrancy Checklist

1. **Every external call happens after all state updates.** No exceptions. Even "read-only" calls.
2. **Every ERC-777 and ERC-1155 interaction treats `send()` and `safeTransferFrom()` as external calls.** They are.
3. **Every contract uses `ReentrancyGuard` on all state-modifying external functions.** Not just the ones with `call{}`.
4. **Multi-function state sharing is protected by a single lock.** Cross-function reentrancy bypasses per-function CEI.
5. **Read-only functions that expose temporarily inconsistent state are documented as potentially unreliable.** Or better, eliminated.

---

## Connection to Other Chapters

- **Ch4 (Flash Loans)**: Flash-loaned funds amplify reentrancy attacks. The CREAM $130M exploit combined flash loan capital with reentrancy to drain lending pools.
- **Ch7 (Token Economics)**: ERC-777 and fee-on-transfer tokens introduce hidden callbacks that create reentrancy vectors. Token integration is security integration.
- **Ch11 (Precision)**: Read-only reentrancy exploits precision mismatches in temporarily inconsistent state. The precision of the inconsistency determines the profitability of the exploit.

---

*Next: Chapter 10 — Initialization & Upgrade Attacks*
