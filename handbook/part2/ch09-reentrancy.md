# Chapter 9: Re-entrancy — The Bug That Never Dies

*"In 2016, TheDAO taught us about re-entrancy. In 2021, Cream Finance taught us we hadn't learned. In 2026, someone will teach us again."*

---

## TheDAO: Genesis of a Vulnerability Class

On June 17, 2016, a contract holding 3.6 million ETH—14% of all Ether in existence at the time—began hemorrhaging funds. The attacker did not exploit a complex economic model or a zero-day in the EVM. They exploited a bug that was known in theory but never seen at scale: a function calling an external address before updating its own state.

TheDAO's `splitDAO()` function followed this pattern:

```solidity
function splitDAO(uint _proposalID, address _newCurator) noEther onlyTokenholders returns (bool) {
    Transfer(msg.sender, 0, balances[msg.sender]);
    withdrawRewardFor(msg.sender);
    
    totalSupply -= balances[msg.sender];
    balances[msg.sender] = 0;   // ← state update AFTER external call
    paidOut[msg.sender] = 0;
    return true;
}
```

`withdrawRewardFor()` called `.call.value()()` to send ETH to `msg.sender`. If `msg.sender` was a contract, its `receive()` function executed before `balances[msg.sender] = 0` ran. The contract's receive function called `splitDAO()` again, which checked the balance—still unchanged—and triggered another withdrawal. Each recursive call drained more ETH before the balance was ever set to zero.

The attacker extracted 3.6 million ETH over several hours. The Ethereum community faced an existential choice: accept the theft as "code is law" or intervene. The community forked. Ethereum Classic continued on the original chain where the theft stood. Ethereum, the chain we use today, rolled back the transaction.

TheDAO cost $60 million. It also cost Ethereum its philosophical innocence. The re-entrancy bug did more than drain money—it forced the entire ecosystem to confront the limits of immutable code.

---

## Anatomy of Re-entrancy

Re-entrancy is not one bug. It is a *class* of bugs with a common root cause: **external calls made before state updates are finalized.**

The EVM is single-threaded. A transaction executes sequentially. But when contract A calls contract B, contract B executes entirely before contract A resumes. If contract B calls back into contract A, it finds the state as it was *before* contract A finished updating. This is not a vulnerability—it is the intended execution model of the EVM. The vulnerability is writing code that assumes external calls will not re-enter.

### The Four Archetypes

**1. Single-Function Re-entrancy (TheDAO)**

The simplest and most common form. A single function makes an external call before updating its state, and the external callee calls that same function again.

```solidity
// VULNERABLE — TheDAO pattern
function withdraw() external {
    uint256 amount = balances[msg.sender];
    (bool ok, ) = msg.sender.call{value: amount}("");  // ← external call
    require(ok);
    balances[msg.sender] = 0;  // ← too late
}
```

**2. Cross-Function Re-entrancy**

The attacker calls function A, which makes an external call. The callee calls function B, which reads state that function A has not yet updated. The two functions share mutable state but have different update sequences.

```solidity
// VULNERABLE — cross-function
mapping(address => uint256) public shares;
mapping(address => uint256) public released;

function withdraw(uint256 amount) external {
    require(shares[msg.sender] >= amount);
    (bool ok, ) = msg.sender.call{value: amount}("");  // ← external call
    require(ok);
    shares[msg.sender] -= amount;  // ← update after call
}

function transfer(address to, uint256 amount) external {
    require(shares[msg.sender] >= amount);
    shares[msg.sender] -= amount;  // ← reads shares before withdraw updates
    shares[to] += amount;
}
```

During the `withdraw` callback, the attacker calls `transfer()`, which reads `shares[msg.sender]` at its pre-withdrawal value. The attacker can transfer tokens they no longer own.

**3. Cross-Contract Re-entrancy (Read-Only)**

The attacker exploits the fact that one contract's state depends on another contract's state, and the other contract can be manipulated during the external call window.

Cream Finance's $130 million exploit in October 2021 exemplified this pattern. Cream's `IronBank` used `yUSDVault` as collateral. The vault's `getPricePerFullShare()` was called during Cream's borrow checks. The attacker flash-loaned assets, deposited them into the vault to manipulate its share price, borrowed against the inflated collateral, and repeated the cycle. The re-entrancy was not in a single contract but across the interaction between Cream's lending logic and Yearn's vault pricing.

**4. Read-Only Re-entrancy**

A newer, subtler variant identified in 2023. The attacker does not modify the victim contract's state—they exploit the fact that the victim reads state that *another* contract is in the process of updating. During a cross-contract call chain, contract A reads from contract B while contract B is mid-update, receiving inconsistent data.

```solidity
// Contract A reads from Contract B
function getCollateralValue(address user) external view returns (uint256) {
    return oracle.getPrice(token) * vault.balanceOf(user);
    // oracle.getPrice() and vault.balanceOf() may be read at different points
    // in contract B's update cycle
}
```

---

## The Check-Effects-Interactions Pattern

The canonical defense against re-entrancy is the Check-Effects-Interactions pattern: verify conditions, update state, then interact with external contracts.

```solidity
// SAFE — checks-effects-interactions
function withdraw(uint256 amount) external {
    // 1. CHECKS
    require(balances[msg.sender] >= amount, "insufficient balance");
    
    // 2. EFFECTS — update state BEFORE external call
    balances[msg.sender] -= amount;
    totalSupply -= amount;
    
    // 3. INTERACTIONS — external call comes LAST
    (bool ok, ) = msg.sender.call{value: amount}("");
    require(ok, "transfer failed");
}
```

If the attacker re-enters, `balances[msg.sender]` is already zero. The attack fails at the `require` check.

This pattern is necessary but not sufficient. It prevents single-function re-entrancy but does not prevent cross-function re-entrancy if multiple functions share the same mutable state and one of them violates the pattern.

### Re-entrancy Guards

For functions that cannot easily follow check-effects-interactions (e.g., functions that must make external calls and then update state based on the result), a re-entrancy guard provides mutual exclusion:

```solidity
// OpenZeppelin ReentrancyGuard
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract SafeVault is ReentrancyGuard {
    function withdraw(uint256 amount) external nonReentrant {
        require(balances[msg.sender] >= amount);
        balances[msg.sender] -= amount;
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok);
    }
}
```

The `nonReentrant` modifier sets a flag on entry and clears it on exit. Any re-entrant call to a function with the same modifier will fail because the flag is already set. This is a blunt instrument—it blocks ALL re-entrant calls, including legitimate ones—but for most contracts, it is the safest default.

The guard's state transition is:

```solidity
modifier nonReentrant() {
    require(_status != _ENTERED, "ReentrancyGuard: reentrant call");
    _status = _ENTERED;   // ← set BEFORE function body
    _;
    _status = _NOT_ENTERED;
}
```

Note that `_status` is set BEFORE the function body executes, not after. This follows check-effects-interactions: the guard updates its own state before the function body makes any external calls.

---

## Cream Finance: When Layers Still Fail

Cream Finance deployed a lending protocol with multiple security layers: re-entrancy guards on every external function, price oracles with deviation checks, and collateral factors that limited borrowing. The October 2021 attack bypassed every layer.

The attack chain:

1. **Flash loan** 500 million DAI from MakerDAO
2. **Deposit** DAI into yUSDVault, inflating the share price
3. **Borrow** against the inflated yUSDVault collateral on Cream's IronBank
4. The borrow function called `yUSDVault.getPricePerFullShare()` to value the collateral
5. The inflated price allowed the attacker to borrow more than the deposit was worth
6. **Repay** the flash loan, keeping the borrowed assets
7. **Repeat** with a second vault, extracting additional funds

Total loss: $130 million.

What Cream's re-entrancy guards did not protect against was manipulation of *external state that the contract relied on for valuation*. The IronBank's state was internally consistent—no double-spend occurred, no balance was incorrectly updated. The vulnerability was that the *information* the contract used to make decisions was manipulated during the external call within the borrow function.

This is why check-effects-interactions is necessary but not sufficient for protocols that depend on external price feeds. Chapter 5 (Oracle Manipulation) covers the oracle-specific defenses required. The re-entrancy guard prevents state corruption; it does not prevent oracle manipulation. The two vulnerability classes combine.

---

## The 2026 Landscape

Re-entrancy was the most exploited vulnerability class from 2016 to 2020. By 2023, it had declined significantly—not because developers stopped making the mistake, but because the tools caught up. Slither's re-entrancy detector, OpenZeppelin's ReentrancyGuard, and Solidity's built-in checks for `send()` and `transfer()` reduced the attack surface.

But re-entrancy did not disappear. It evolved:

| Year | Exploit | Amount | Variant |
|------|---------|:------:|---------|
| 2016 | TheDAO | $60M | Single-function |
| 2020 | Uniswap/Lendf.Me | $25M | ERC-777 callback |
| 2021 | Cream Finance | $130M | Cross-contract + oracle |
| 2022 | Fei Protocol | $80M | Flash loan + re-entrancy |
| 2022 | Rari Capital | $80M | Cross-function |
| 2023 | Exactly Protocol | $7M | Read-only re-entrancy |

The variants grow more subtle. TheDAO was a textbook single-function re-entrancy. Cream combined re-entrancy with oracle manipulation and flash loans—three vulnerability classes in one attack. Exactly Protocol introduced read-only re-entrancy, where no state was corrupted but inconsistent reads allowed exploitation.

The pattern is clear: **re-entrancy never dies. It combines with whatever new primitive emerges.** In 2020, it combined with ERC-777 callbacks. In 2021, with Yearn vaults. In 2022, with flash loans. In 2026, the combination targets are AI agent wallets (see Chapter 21) and cross-chain message verification (see Chapter 8).

---

## Detection: What Scanners See (and Miss)

### What Automated Scanners Detect

```python
# Slither's re-entrancy detector (simplified logic)
# Flags: external call → state write where state write appears AFTER the call
# Misses: cross-contract, read-only, flash loan chains
```

**Slither** detects single-function re-entrancy with high accuracy (~95% true positive rate) but misses cross-function and cross-contract variants.

**Mythril** uses symbolic execution to explore call chains and can detect some cross-function re-entrancy patterns, but the state space explosion limits its depth.

**Our 58-rule scanner** detects re-entrancy with three patterns:

```python
"reentrancy_single": {
    "regex": [r'\.call\{value:.*\}\(.*\).*\n.*= 0', r'\.send\(.*\).*\n.*= 0'],
    "severity": "CRITICAL",
    "description": "State update after external call — classic re-entrancy",
    "fix": "Move state update BEFORE external call (check-effects-interactions)"
},
"reentrancy_no_guard": {
    "regex": [],
    "severity": "HIGH",
    "description": "External call in nonReentrant-guarded function (manual review required)",
    "negated": ["nonReentrant", "ReentrancyGuard", "locked"]
},
"reentrancy_cross_function": {
    "regex": [],
    "severity": "CRITICAL",
    "description": "Multiple functions sharing mutable state with external calls",
    "requires_manual": True
}
```

### What All Scanners Miss

1. **Cross-contract re-entrancy**: No static analyzer can trace state dependencies across contract boundaries at scale. This requires manual review.

2. **Read-only re-entrancy**: No state corruption occurs, so mutation-based detectors produce no alerts. This is purely a logic vulnerability.

3. **Flash loan + re-entrancy chains**: The re-entrancy is just one link in an attack chain that includes flash loans, oracle manipulation, and governance attacks. Pattern matching on re-entrancy alone misses the forest for the tree.

### Manual Review Checklist

When reviewing a contract that makes external calls, ask:

```
□ Does the function call an external contract before updating its own state?
  → If yes, this is a re-entrancy risk.

□ Does any OTHER function read the same state variable?
  → If yes, cross-function re-entrancy is possible.

□ Does the external call invoke a contract whose behavior can be manipulated?
  → ERC-777 tokens, vault share prices, oracle feeds—all manipulable.

□ Does the function read external state (oracle, vault, pool) for its logic?
  → If yes, the external state may be inconsistent during re-entrancy.

□ Does the contract use nonReentrant on ALL external-facing functions?
  → A single unguarded function can enable cross-function re-entrancy.

□ Does the contract use a proxy pattern?
  → Upgradeable contracts can introduce re-entrancy in new implementations that did not
    exist in the original. Every upgrade requires re-auditing for this class.
```

---

## Fix Patterns

### Pattern 1: Pull Over Push

Instead of pushing ETH to users, let users pull it:

```solidity
// ❌ PUSH — vulnerable to re-entrancy
function withdraw() external {
    uint256 amount = balances[msg.sender];
    balances[msg.sender] = 0;
    (bool ok, ) = msg.sender.call{value: amount}("");  // ← still an external call
    require(ok);
}

// ✅ PULL — no external call in withdrawal
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount);
    balances[msg.sender] -= amount;
    pendingWithdrawals[msg.sender] += amount;
    // User calls claim() separately to receive ETH
}

function claim() external {
    uint256 amount = pendingWithdrawals[msg.sender];
    pendingWithdrawals[msg.sender] = 0;
    (bool ok, ) = msg.sender.call{value: amount}("");
    require(ok);
}
```

The pull pattern separates state update from value transfer. Even if `claim()` is re-entered, `pendingWithdrawals[msg.sender]` is already zero.

### Pattern 2: ReentrancyGuard + Check-Effects-Interactions

The strongest defense combines both:

```solidity
contract UltraSafeVault is ReentrancyGuard {
    mapping(address => uint256) public balances;
    mapping(address => uint256) public pending;
    
    function withdraw(uint256 amount) external nonReentrant {
        // 1. CHECKS
        require(balances[msg.sender] >= amount, "insufficient");
        
        // 2. EFFECTS
        balances[msg.sender] -= amount;
        pending[msg.sender] += amount;
        
        // 3. INTERACTIONS (after all state is consistent)
        // Moved to claim() — pull pattern
    }
    
    function claim() external nonReentrant {
        uint256 amount = pending[msg.sender];
        require(amount > 0, "nothing to claim");
        
        pending[msg.sender] = 0;  // ← EFFECTS first
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "claim failed");
    }
}
```

### Pattern 3: Untrusted Token Handling

When your contract must interact with arbitrary ERC-20 tokens (which may be malicious):

```solidity
function swap(address tokenIn, address tokenOut, uint256 amountIn) external nonReentrant {
    // Assume tokenIn is potentially malicious
    uint256 balanceBefore = IERC20(tokenOut).balanceOf(address(this));
    
    IERC20(tokenIn).transferFrom(msg.sender, address(this), amountIn);
    // ↑ This is an external call to untrusted code
    // If tokenIn is an ERC-777, transferFrom triggers tokensToSend() callback
    // During the callback, ALL state must be consistent
    
    uint256 balanceAfter = IERC20(tokenOut).balanceOf(address(this));
    uint256 amountOut = balanceAfter - balanceBefore;
    
    IERC20(tokenOut).transfer(msg.sender, amountOut);
}
```

The key: use balance deltas rather than relying on internal accounting during the external call window. The attacker can re-enter, but the delta calculation is based on actual token balances, which are updated atomically by the token contract.

---

## Connection to Other Chapters

Re-entrancy rarely works alone. In the 63-exploit database, over 60% of re-entrancy attacks combine with at least one other vulnerability class:

- **Ch4 (Flash Loans)**: The flash loan provides the capital; re-entrancy provides the execution window. Without flash loans, many re-entrancy attacks would require capital the attacker doesn't have.

- **Ch5 (Oracle Manipulation)**: Cream Finance teaches that re-entrancy in a function that reads external prices combines with oracle manipulation. The re-entrancy guard protects state; it does not protect against bad input data.

- **Ch8 (Cross-Chain)**: Bridge message verification is a re-entrancy target. A bridge that processes messages sequentially and makes external calls during processing is re-entrant—the external callee can submit another message before the first is marked as processed.

- **Ch21 (AI Agent Security)**: AI agents that manage on-chain positions make autonomous external calls. If an agent's execution model does not enforce check-effects-interactions, a malicious contract can re-enter the agent's logic and drain its wallet. The agent's "reasoning" about its state is invalidated during the re-entrancy window.

---

## Summary

Re-entrancy is DeFi's oldest vulnerability class and its most persistent. The fundamental issue—external calls before state finalization—is baked into the EVM's execution model. Every new DeFi primitive creates new re-entrancy surfaces. Every new combination of protocols creates new cross-contract re-entrancy paths.

The defenses are well-understood: check-effects-interactions, ReentrancyGuard, pull-over-push, balance deltas. The challenge is not knowing the defenses—it is applying them consistently across every external call in every contract, including contracts that are upgraded, composed, or integrated with new protocols.

TheDAO taught us the pattern. Cream taught us the cross-contract variant. The next major re-entrancy exploit will teach us the next variant. It will not be because the defense was unknown. It will be because someone, somewhere, forgot to apply it.

> *"Re-entrancy is not a bug you fix once. It is a discipline you maintain forever."*
