# Chapter 10: Initialization & Upgrade Attacks

*"Upgradeable contracts solve one problem and create ten more. The most dangerous one is invisible until someone exploits it."*

---

## The Uranium Incident

On April 28, 2021, the Uranium Finance protocol on Binance Smart Chain was exploited for $50 million. The attack was not a flash loan manipulation. It was not a price oracle failure. It was not a reentrancy.

The Uranium protocol used an upgradeable proxy pattern. The implementation contract — the one that contained the actual logic — had an `initialize()` function that set the contract's owner. This `initialize()` function had no access control. It was supposed to be called once, during deployment of the proxy, which would delegate the call to the implementation.

Someone — it is still not clear who — called `initialize()` directly on the implementation contract. They became the owner. As the owner, they upgraded the proxy to a malicious implementation that transferred all user funds to an address they controlled.

$50 million. One missing modifier.

The Uranium exploit is the defining case study of initialization attacks because it demonstrates a pattern that keeps recurring: **developers think initialization happens once, at deployment time, and don't protect it from being called again.**

---

## Why Upgradeable Contracts Exist

Smart contracts are supposed to be immutable. Code deployed to an address can never be changed. This is a feature — you can trust that the code will execute exactly as written, forever.

But immutability has a cost. Bugs cannot be fixed after deployment. Features cannot be added. Security vulnerabilities discovered after launch cannot be patched.

The proxy pattern solves this by separating the contract into two pieces:

1. **Proxy contract**: Holds the state (balances, owner, all storage variables). Its single job is to delegate every call to the implementation.
2. **Implementation contract**: Contains the logic. Can be replaced by pointing the proxy at a new implementation.

Users interact with the proxy. The proxy delegates to the implementation. The implementation can be swapped without changing the proxy's address or state.

This is elegant. It is also a breeding ground for a specific class of vulnerabilities that only exist because of this indirection.

---

## Pattern #21: Unprotected Initializer

**Severity**: HIGH
**Real case**: Uranium $50M, numerous smaller incidents

### The Vulnerability

The implementation contract has an `initialize()` function that sets critical state — owner, fee parameters, oracle addresses — without any protection against being called a second time or being called by an unauthorized address.

```solidity
// ❌ VULNERABLE: No access control on initialize()
function initialize(address _owner) external {
    owner = _owner;
    feeRecipient = _owner;
    maxFee = 100;
}
```

Anyone who calls this function on the implementation contract becomes the owner. Not of the proxy — of the *implementation.* When the proxy delegates to the implementation, it uses the implementation's storage. Whoever owns the implementation controls every proxy that delegates to it.

### Why It Keeps Happening

The OpenZeppelin library provides an `initializer` modifier that prevents a function from being called more than once:

```solidity
function initialize() external initializer {
    __Ownable_init();
}
```

But the `initializer` modifier only protects against double-calling through the proxy's context. If someone calls `initialize()` directly on the implementation — bypassing the proxy entirely — the modifier's storage is the implementation's storage, not the proxy's. The attack succeeds because the proxy never set the "initialized" flag.

### The Fix

OpenZeppelin 4.5+ provides `_disableInitializers()` which must be called in the implementation's constructor:

```solidity
// ✅ SAFE: Disables initializers on the implementation
constructor() {
    _disableInitializers();
}

function initialize() external initializer {
    __Ownable_init();
}
```

This prevents anyone from calling `initialize()` on the implementation contract directly. The function can only be called through the proxy's context.

---

## Pattern #22: Storage Collision During Upgrade

**Severity**: CRITICAL

### The Vulnerability

The proxy and implementation share the same storage layout. If the implementation's storage layout changes during an upgrade — a variable is added, removed, or reordered — the proxy's state becomes corrupt.

```solidity
// v1 implementation
contract V1 {
    uint256 public ownerSlot;      // Storage slot 0
    uint256 public feeSlot;        // Storage slot 1
}

// v2 implementation (BROKEN)
contract V2 {
    address public ownerSlot;      // Storage slot 0 — overwritten as address!
    uint256 public newVariable;    // Storage slot 1 — reads old feeSlot!
    uint256 public feeSlot;        // Storage slot 2 — now empty!
}
```

When the proxy upgrades from V1 to V2, slot 0 (a `uint256`) is now interpreted as an `address`. The old data is still there — it just means something completely different. The protocol is broken, and the funds may be unrecoverable.

### The Fix

Use storage gaps and inherited storage contracts:

```solidity
contract V1 is Initializable {
    uint256 public ownerSlot;
    uint256 public feeSlot;
    uint256[50] private __gap;  // Reserved for future variables
}

contract V2 is V1 {
    uint256 public newVariable;  // Uses the first gap slot
    // gap shrinks to 49 slots
}
```

Every contract in the inheritance chain must leave gap space for future versions. The gap acts as a buffer — new variables fill the buffer instead of overwriting existing state.

---

## Pattern #23: Beacon Proxy Attack

**Severity**: HIGH

### The Vulnerability

A beacon proxy pattern uses a central beacon contract that holds the current implementation address. Every proxy reads the beacon to determine which implementation to delegate to. If the beacon's implementation is upgraded, every proxy changes behavior simultaneously.

The beacon's `upgrade()` function is the single point of failure for every proxy in the system.

### The Attack

1. Attacker compromises the beacon's admin key
2. Attacker upgrades the beacon to a malicious implementation
3. Every proxy — potentially hundreds or thousands — now executes the attacker's code
4. All user funds in all proxies are drained simultaneously

### The Fix

The beacon's upgrade function must have the strongest possible access control: multi-sig, timelock, and per-proxy opt-in rather than forced upgrade.

---

## Pattern #24: Selfdestruct and CREATE2 Re-deployment

**Severity**: HIGH
**Real case**: Metamorphic contract attacks

### The Vulnerability

`CREATE2` deploys a contract at a deterministic address based on the deployer's address, a salt, and the contract's init code. If a contract deployed with `CREATE2` calls `selfdestruct`, a different contract can be deployed at the same address using the same deployer and salt.

Users who trust the address because it previously contained legitimate code may now interact with malicious code at the same address.

### The Fix

Never use `selfdestruct` in contracts deployed with `CREATE2`. If selfdestruct is required for operational reasons, prevent re-deployment by tracking deployed salts.

---

## The Upgrade Security Checklist

1. **Is `_disableInitializers()` called in the implementation's constructor?** If not, Uranium can happen again.
2. **Does every contract in the inheritance chain have storage gaps?** Count the gaps before each upgrade.
3. **Is the upgrade process timelocked?** No instant upgrades, no single-key.
4. **Is the beacon protected by multi-sig?** A single key controls every proxy.
5. **Are users notified before upgrades?** They have the right to exit before the rules change.

---

*Next: Chapter 11 — Precision, Arithmetic & Gas Attacks*
