# Chapter 10: Initialization & Upgrade Attacks

*"Upgradeable contracts solve the immutability problem. They also create a new class of vulnerability that immutability was designed to prevent."*

---

## The Uranium Incident: April 28, 2021

Uranium Finance was a yield farming protocol on Binance Smart Chain. On April 28, 2021, less than two weeks after launch, it was exploited for $50 million. The attack was not a flash loan. It was not an oracle manipulation. It was not a reentrancy.

The protocol used a standard upgradeable proxy pattern: a proxy contract that delegates all calls to an implementation contract. The implementation contract contained the business logic—deposits, withdrawals, reward calculations—and an `initialize()` function that set critical parameters:

```solidity
function initialize(address _owner) external {
    owner = _owner;
    feeRecipient = _owner;
    rewardRate = 1000;
}
```

This function was supposed to be called once, during deployment, through the proxy. The proxy would delegate the call to the implementation, the implementation would set `owner` to the deployer's address, and the `initializer` modifier would prevent it from being called again.

But someone called `initialize()` directly on the implementation contract, bypassing the proxy entirely. The `initializer` modifier's storage lived in the implementation's own storage—not the proxy's. From the implementation's perspective, the function had never been called. It executed without complaint. The caller became the owner.

As the owner, they upgraded the proxy to point to a malicious implementation that transferred all user funds to their address. The entire protocol was drained in a single transaction chain.

$50 million. One missing `_disableInitializers()`.

### The Deeper Lesson

The Uranium exploit reveals a fundamental tension in upgradeable contract design: the implementation contract is not supposed to be interacted with directly, but it must exist on-chain, with all its functions publicly callable. The only protection is a storage flag that the implementation itself cannot reliably enforce.

OpenZeppelin addressed this in version 4.5 by adding `_disableInitializers()`, which must be called in the implementation's constructor. The constructor runs during deployment, before any external caller can interact with the contract. Once disabled, the implementation's initializers can never be called directly.

But the pattern persists in unaudited forks and custom proxy implementations. Every new DeFi protocol that deploys an upgradeable contract without `_disableInitializers()` in the constructor is Uranium waiting to happen.

---

## Why Upgrades Are Dangerous

Immutability was a deliberate design choice in Ethereum. A contract's code, once deployed, could never be changed. Users could verify the code once and trust it forever. Developers could not change the rules after users had committed funds.

Upgradeable proxies break this guarantee. The contract's address stays the same, but the code at that address can change at any time. From the user's perspective, the contract they audited yesterday might not be the contract executing their transaction today.

This creates an entirely new attack surface:

1. **The upgrade function itself**: If an attacker can call the upgrade function, they can replace the entire protocol with their own code.
2. **The implementation contract**: Directly accessible, potentially uninitialized, with functions that were never meant to be called.
3. **Storage collisions**: When the implementation changes, the new code's storage layout must match the old code's exactly. One misaligned variable corrupts the entire state.
4. **The proxy admin**: A single entity controls every upgrade. If that entity is compromised, every user of every proxy is compromised.

---

## Pattern #21: Unprotected Initializer

**Severity**: HIGH
**Real case**: Uranium $50M

### The Vulnerability

```solidity
// ❌ VULNERABLE: No protection against direct calls
contract ImplementationV1 {
    address public owner;
    bool public initialized;
    
    function initialize() external {
        require(!initialized, "Already initialized");
        owner = msg.sender;
        initialized = true;
    }
    // Missing: _disableInitializers() in constructor
}
```

An attacker calls `initialize()` directly on the implementation. The `initialized` flag is the implementation's storage, not the proxy's. The call succeeds. The attacker becomes the owner. The attacker upgrades the proxy to a malicious implementation.

### The Fix

```solidity
// ✅ SAFE: Constructor disables direct initialization
contract ImplementationV1 {
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }
    
    function initialize() external initializer {
        // _disableInitializers() ensures this can only be called through proxy
        __Ownable_init();
    }
}
```

---

## Pattern #22: Storage Collision During Upgrade

**Severity**: CRITICAL

### The Vulnerability

The proxy and implementation share the same storage layout. When a new implementation is deployed, its variables must occupy the exact same storage slots as the previous implementation. Adding, removing, or reordering variables corrupts the state.

```solidity
// V1: Deployed on mainnet
contract V1 {
    uint256 public totalSupply;    // Slot 0
    uint256 public reserveBalance; // Slot 1
}

// V2: Intended upgrade — BROKEN
contract V2 {
    uint256 public totalSupply;     // Slot 0 — OK
    uint256 public newVariable;     // Slot 1 — READS OLD reserveBalance!
    uint256 public reserveBalance;  // Slot 2 — NEW, empty
}
```

After upgrading from V1 to V2:
- `totalSupply` at slot 0: correct
- `newVariable` at slot 1: reads V1's `reserveBalance` value—which represents a completely different meaning
- `reserveBalance` at slot 2: zero, because it's a new slot

The protocol's accounting is now permanently corrupted. Users can withdraw more than they deposited or less than they are owed. The only fix is a complete re-deployment.

### The Fix

Use storage gaps:

```solidity
contract V1 is Initializable {
    uint256 public totalSupply;
    uint256 public reserveBalance;
    uint256[50] private __gap;  // Reserved for future variables
}

contract V2 is V1 {
    uint256 public newVariable;  // Occupies the first gap slot
    // gap shrinks to 49 slots. No collision.
}
```

Every contract in the inheritance chain must include gaps. OpenZeppelin recommends 50 slots per contract.

---

## Pattern #23: Beacon Proxy Single Point of Failure

**Severity**: HIGH

### The Vulnerability

A beacon proxy pattern centralizes the implementation address in a single beacon contract. Every proxy reads the beacon to determine which implementation to use. If the beacon's implementation is changed, every proxy changes behavior simultaneously.

```solidity
// ❌ VULNERABLE: Single key controls all proxies
function upgrade(address newImpl) external onlyOwner {
    implementation = newImpl;
    // EVERY proxy now points to newImpl
}
```

The beacon's `onlyOwner` is a single point of failure for every proxy in the system.

### The Fix

Beacon upgrades must have the strongest possible access control:

```solidity
function scheduleUpgrade(address newImpl) external onlyMultisig {
    scheduledImpl = newImpl;
    scheduledTime = block.timestamp + 48 hours;
    emit UpgradeScheduled(newImpl, scheduledTime);
}

function executeUpgrade() external {
    require(block.timestamp >= scheduledTime, "Timelock not expired");
    require(block.timestamp <= scheduledTime + 24 hours, "Expired");
    implementation = scheduledImpl;
}
```

---

## Pattern #24: selfdestruct and CREATE2 Re-deployment

**Severity**: HIGH
**Real case**: Metamorphic contract attacks

### The Vulnerability

`CREATE2` deploys a contract at a deterministic address based on `(deployer, salt, initcode)`. If a contract deployed with `CREATE2` calls `selfdestruct`, a different contract can be deployed at the same address using the same deployer and salt.

Users trust the address because it previously contained legitimate code. Now it contains malicious code. The address is the same. The contract is completely different.

### The Fix

Never use `selfdestruct` in contracts deployed with `CREATE2`. If selfdestruct is required for operational reasons, track deployed salts and block re-deployment.

---

## The Parity Wallet Incident: November 6, 2017

On November 6, 2017, a developer named "devops199" called `initWallet()` on the Parity multi-sig wallet library contract. The library was shared by hundreds of wallets, each delegating to it for their implementation logic. The library had no owner—it was never initialized.

`devops199` became the owner. They then called `kill()` on the library, triggering `selfdestruct`. The library's code was deleted from the blockchain. Every wallet that depended on the library—including wallets holding a combined $150 million—was permanently frozen. The wallets were intact. The ETH was still there. But the code needed to move it no longer existed.

The Parity freeze is not a typical exploit—the attacker did not profit, the funds were not stolen. But it is the definitive case study in why **shared implementation contracts must never be directly callable.** The library was a public good. Anyone could interact with it. One person's mistake froze $150 million forever.

---

## The Upgrade Security Checklist

1. **Every implementation constructor calls `_disableInitializers()`.** If not, the code is Uranium.
2. **Every contract in the inheritance chain has storage gaps.** Count the gaps before every upgrade.
3. **Upgrade functions have a minimum 48-hour timelock.** Users have the right to exit before the rules change.
4. **Beacon upgrades require multi-sig with organizational diversity.** A single key should never control every proxy.
5. **Never `selfdestruct` a contract deployed with `CREATE2`.** Address reuse is not theoretical.
6. **Implementation contracts are not documentation.** They are live, publicly callable contracts. Treat them as such.

---

## Connection to Other Chapters

- **Ch6 (Access Control)**: The Uranium and Parity attacks are access control failures. The vulnerability was not in the upgrade mechanism—it was in the assumption that certain functions would never be called.
- **Ch11 (Precision)**: Storage collisions during upgrades are precision errors at the architectural level—a variable at slot 1 means one thing in V1 and a completely different thing in V2.
- **Ch12 (Governance)**: The upgrade admin is a governance function. Who controls the upgrade? Who controls them? These are governance questions, not technical ones.

---

*Next: Chapter 11 — Precision, Arithmetic & Gas Attacks*
