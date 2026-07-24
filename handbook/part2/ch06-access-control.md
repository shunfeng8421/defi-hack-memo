# Chapter 6: Access Control Failures

*"The most expensive bug in DeFi history was not a bug. It was a function that anyone could call."*

---

## The PolyNetwork Lesson

On August 10, 2021, an attacker discovered that a function on the PolyNetwork bridge contract — a function that transferred custody of cross-chain assets — had no access control. No `onlyOwner`. No `require(msg.sender == admin)`. No signature verification.

The function was designed to be called by the protocol's admin to move funds between chains. But because nobody had added an access control check, *anyone* could call it.

The attacker called it. They transferred $610 million worth of assets to addresses they controlled.

$610 million. One missing `onlyOwner`.

The story had an unusual ending. The attacker returned the funds after a negotiation with the PolyNetwork team, claiming they wanted to "expose the vulnerability" rather than steal the money. But the lesson stands: **access control is not a feature you add. It is the default state that every function must opt out of.**

---

## Pattern #8: Missing Access Control

**Severity**: HIGH
**Real cases**: PolyNetwork $610M, numerous smaller incidents

### The Vulnerability

A function performs a privileged operation — transferring funds, upgrading the implementation, changing protocol parameters — without checking who is calling it.

```solidity
// ❌ VULNERABLE: Anyone can upgrade the contract
function upgrade(address newImplementation) external {
    _upgradeTo(newImplementation);
}
```

This is the simplest vulnerability in DeFi. It requires no exploit path, no manipulation, no flash loan. It requires only that someone finds the function.

### Why It Happens

Missing access control is almost never a coding error. It is a process error. The developer intended to add access control. They wrote the function, planned to add the modifier later, and shipped the contract before adding it.

This is why static analysis tools like Slither flag every public function without a modifier. The tool doesn't know that a function is "supposed to be public." It only knows that it *can be called by anyone.*

### The Fix

```solidity
// ✅ SAFE: Access control via modifier
function upgrade(address newImplementation) external onlyOwner {
    _upgradeTo(newImplementation);
}

modifier onlyOwner() {
    require(msg.sender == owner, "Not owner");
    _;
}
```

Or for more granular control:

```solidity
function upgrade(address newImplementation) external onlyRole(UPGRADER_ROLE) {
    _upgradeTo(newImplementation);
}
```

---

## Pattern #9: Admin Key Privilege Escalation

**Severity**: HIGH
**Real case**: Ronin Bridge $625M

Having an admin key is not a vulnerability. Having an admin key without a timelock, without multi-sig, and without monitoring — that is a vulnerability.

### The Attack

The Ronin Bridge used a 5-of-9 validator multi-sig to authorize cross-chain withdrawals. The attacker compromised five validator keys through a combination of social engineering and credential theft. Because there was no timelock on withdrawals — validators could authorize and execute in the same transaction — the attacker drained $625 million before anyone could react.

### The Design Principle

Every privileged operation must have a delay between authorization and execution:

```solidity
// ❌ VULNERABLE: Instant upgrade
function upgrade(address impl) external onlyOwner {
    _upgradeTo(impl);  // Immediately executes
}

// ✅ SAFE: Timelocked upgrade
function scheduleUpgrade(address impl) external onlyOwner {
    scheduledExecution[keccak256(abi.encode(impl))] = block.timestamp + 48 hours;
}

function executeUpgrade(address impl) external {
    require(block.timestamp >= scheduledExecution[keccak256(abi.encode(impl))]);
    _upgradeTo(impl);
}
```

The timelock serves a second purpose beyond preventing instant attacks: it gives users time to exit. If a malicious upgrade is scheduled, users have 48 hours to withdraw their funds before the upgrade executes. This is the principle of "no surprises" — users should never wake up to find the protocol they trusted has changed without warning.

---

## Pattern #10: Unprotected Selfdestruct

**Severity**: CRITICAL

The `selfdestruct` opcode deletes a contract's code and sends its balance to a specified address. If a contract has a `selfdestruct` function with inadequate access control, the entire protocol's funds can be permanently destroyed.

```solidity
// ❌ VULNERABLE
function kill() external onlyOwner {  // Single key!
    selfdestruct(payable(msg.sender));
}
```

### The Fix

Never use `selfdestruct` in upgradeable contracts. For non-upgradeable contracts, require multi-sig and timelock:

```solidity
// ✅ SAFE: Requires multi-sig + timelock + community notification
function initiateKill() external onlyMultisig {
    killScheduledAt = block.timestamp;
    emit KillScheduled(48 hours);
}

function executeKill() external onlyMultisig {
    require(block.timestamp >= killScheduledAt + 48 hours);
    selfdestruct(payable(treasury));
}
```

---

## Pattern #11: Delegatecall to User-Controlled Address

**Severity**: CRITICAL
**Real case**: Parity Wallet $150M freeze (2017)

`delegatecall` executes code from another contract in the context of the calling contract. It preserves `msg.sender`, `msg.value`, and — most importantly — storage access.

If the target address of a `delegatecall` is user-supplied, the user can provide a contract that modifies any storage slot of the calling contract.

```solidity
// ❌ VULNERABLE: User controls the delegatecall target
function execute(address target, bytes calldata data) external {
    (bool success,) = target.delegatecall(data);
    require(success);
}
```

### The Parity Wallet Incident

The Parity multi-sig wallet used a library contract for its implementation. The library was not initialized with an owner. An attacker called `initWallet()` on the library — setting themselves as the owner — then called `kill()` to `selfdestruct` the library. Every wallet that depended on that library was permanently frozen because the library's code was deleted from the chain.

$150 million worth of ETH remains frozen to this day.

### The Fix

The address used in `delegatecall` must be stored in the contract's own storage and set through a timelocked, multi-sig process:

```solidity
// ✅ SAFE: Implementation address stored in contract storage
address public implementation;

function setImplementation(address impl) external onlyTimelock {
    implementation = impl;
}

fallback() external payable {
    address impl = implementation;
    require(impl != address(0), "No implementation");
    assembly {
        calldatacopy(0, 0, calldatasize())
        let result := delegatecall(gas(), impl, 0, calldatasize(), 0, 0)
        returndatacopy(0, 0, returndatasize())
        switch result
        case 0 { revert(0, returndatasize()) }
        default { return(0, returndatasize()) }
    }
}
```

---

## Pattern #12: Hidden Owner Backdoor

**Severity**: CRITICAL

Some protocols implement "emergency" functions that grant the owner unlimited power. These functions are often hidden behind innocuous names:

```solidity
function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
    IERC20(token).transfer(owner, amount);  // Drains any token
}

function setFee(uint256 newFee) external onlyOwner {
    fee = newFee;  // Can be set to 100%
}
```

The existence of these functions means that any single-key compromise results in total loss. The functions may be legitimate — emergency withdrawal is a real operational need — but their existence without adequate safeguards creates a backdoor.

### The Fix

Emergency functions must have proportional restrictions:

```solidity
// ✅ SAFE: Emergency withdrawal with limits
function emergencyWithdraw(address token, uint256 amount) external onlyMultisig {
    require(amount <= totalValue * 10 / 100, "Max 10% emergency");  // Cap
    require(block.timestamp >= lastEmergency + 7 days, "Cooldown");  // Rate limit
    lastEmergency = block.timestamp;
    IERC20(token).transfer(treasury, amount);
}
```

---

## The Access Control Detector

| Pattern | Name | Detection |
|:--:|------|------|
| 8 | Missing Access | Public + sensitive + no modifier |
| 9 | Admin Privilege | Single key + no timelock |
| 10 | Selfdestruct | `selfdestruct` + single key |
| 11 | Delegatecall | Delegatecall + user address |
| 12 | Hidden Backdoor | Owner + drain + no timelock |

---

## The Access Control Checklist

Before deploying:

1. **Every state-changing function**: Who can call it? Document the answer.
2. **Every `onlyOwner` function**: Is there a timelock? Is it multi-sig?
3. **Every emergency function**: What limits its blast radius?
4. **Every upgrade function**: What notification do users receive?

---

*Next: Chapter 7 — Token Economics Attacks*
