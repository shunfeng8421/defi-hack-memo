// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Proxy Vulnerability Lab — 8 Common Proxy Attack Vectors
/// @notice 80% of DeFi uses upgradeable proxies. None are systematically audited.
/// @author Shiqiang Chen · July 2026

// ============================================================
// #1: UUPS — Uninitialized Implementation (CRITICAL)
// ============================================================
contract Attack1_UUPS_UninitializedImpl {
    // VULNERABLE: Implementation contract's initialize() has no access control
    // Attack: Call initialize() on the implementation directly → become owner
    // Real case: Wormhole $326M (partially via proxy upgrade)
    
    address public owner;
    bool private _initialized;
    
    function initialize() external {
        // BUG: No onlyProxy check, no _initialized guard in some versions
        require(!_initialized, "Already initialized");
        owner = msg.sender; // Anyone can call if directly on implementation!
        _initialized = true;
    }
    
    // FIX: Use _disableInitializers() in constructor
    // constructor() { _disableInitializers(); }
}

// ============================================================
// #2: Storage Collision (CRITICAL)
// ============================================================
contract Attack2_StorageCollision {
    // VULNERABLE: Implementation v1 has "uint256 owner" at slot 0
    // Implementation v2 has "address admin" at slot 0 → overwrites owner!
    // Attack: Upgrade changes storage layout → corrupts critical state
    
    // v1 layout:
    uint256 public slot0_v1; // slot 0
    
    // v2 layout (WRONG — storage collision!):
    // address public slot0_v2; // slot 0 — COLLIDES with uint256 above
    
    // FIX: Use inherited storage gaps or diamond storage pattern
    // uint256[50] private __gap;
}

// ============================================================
// #3: Transparent Proxy — Selector Clash (HIGH)
// ============================================================
contract Attack3_SelectorClash {
    // VULNERABLE: Admin function has same 4-byte selector as implementation function
    // Transparent proxy checks: if (msg.sender == admin) → fall through to admin
    // Attack: Craft call with matching selector → call admin function instead of impl
    
    // Admin function:
    function upgradeTo(address) external {} // selector: 0x3659cfe6
    
    // Implementation function (if same selector exists):
    // function someBusinessLogic(address) external {} // selector: 0x3659cfe6 → CLASH!
    
    // FIX: Use UUPS or separate admin contract
}

// ============================================================
// #4: Diamond Proxy — Facet Selector Override (HIGH)
// ============================================================
contract Attack4_DiamondFacet {
    // VULNERABLE: Adding a new facet with overlapping selectors
    // Diamond proxy resolves: facet A has selector 0xABCD, facet B also has 0xABCD
    // Attack: Add malicious facet that overrides existing function selector
    
    // struct FacetCut { address facet; bytes4[] selectors; }
    // diamondCut([FacetCut({facet: attacker, selectors: [existingSelector]})], ...)
    // → Attacker's facet now handles that selector
    
    // FIX: Validate no selector overlap on diamondCut
}

// ============================================================
// #5: Beacon Proxy — Implementation Swap (HIGH)
// ============================================================
contract Attack5_BeaconSwap {
    // VULNERABLE: Beacon owner can change implementation for ALL proxy instances
    // Attack: Single beacon.update() → corrupt all deployed proxies
    // Real case: Affects OpenZeppelin BeaconProxy users
    
    address public implementation;
    
    // BUG: No timelock, single key, instant effect on all proxies
    function update(address _newImpl) external {
        require(msg.sender == owner);
        implementation = _newImpl; // All proxies now point to malicious code
    }
    
    address owner;
}

// ============================================================
// #6: Metamorphic Contract — CREATE2 Re-deploy (MEDIUM)
// ============================================================
contract Attack6_Metamorphic {
    // VULNERABLE: CREATE2 + selfdestruct → redeploy different code at same address
    // 1. Deploy contract A at CREATE2 address
    // 2. Contract A.selfdestruct()
    // 3. Deploy contract B at same CREATE2 address
    // 4. Users trust the address → now different code exists there
    
    // Attack: Impersonate a known-good contract address
    // FIX: Never trust addresses; always verify code hash
}

// ============================================================
// #7: Delegatecall to Self (MEDIUM)
// ============================================================
contract Attack7_SelfDelegatecall {
    // VULNERABLE: contract calls delegatecall(address(this), data)
    // context: msg.sender, msg.value preserved but code changes
    // Attack: If storage layout changes between implementation versions
    
    fallback() external payable {
        // BUG: delegatecall to self can cause storage corruption with partial upgrades
        address impl = getImplementation();
        (bool ok,) = impl.delegatecall(msg.data);
        require(ok);
    }
    
    function getImplementation() internal view returns (address) {
        // Some storage-based implementation resolution
        return address(0);
    }
}

// ============================================================
// #8: Unprotected Initializer in Inherited Contract (CRITICAL)
// ============================================================
contract Attack8_InheritedInit {
    // VULNERABLE: Parent contract has initialize() without onlyProxy
    // Child inherits parent → parent.initialize() can be called arbitrarily
    // Attack: Call initialize() on child → set parent's admin to attacker
    
    // FIX: Chain initializer: only one __init() per chain, all with onlyInitializing
    // function initialize() public initializer {
    //     __Parent_init();
    //     __Child_init();
    // }
}

// ============================================================
// Summary
// ============================================================
/// @title Proxy Attack Patterns
/// @dev 80% of DeFi uses proxies — these 8 patterns cover the known attack surface
/// Real losses: $326M (Wormhole), $50M (Uranium), $30M (Spartan)
