# Chapter 6: Access Control Failures

*"The most expensive bug in DeFi history was not a bug. It was a function that anyone could call."*

---

## The PolyNetwork Lesson

On August 10, 2021, an anonymous security researcher—or attacker, depending on who you ask—discovered something extraordinary. The PolyNetwork bridge, a cross-chain protocol holding $610 million in user assets, had a function that transferred custody of those assets between chains. This function did exactly what it was designed to do. What it was not designed to do was let anyone call it.

The function lacked an access control modifier. No `onlyOwner`. No `require(msg.sender == admin)`. No signature verification. The developer had intended to add one—the function name suggested restricted access—but in the rush to deploy, the modifier was never added.

The researcher called the function. They transferred $610 million to addresses they controlled. The entire exploit was a single transaction containing a single function call that should have been impossible.

The money was eventually returned after a surreal negotiation conducted through Ethereum transaction messages. The researcher claimed they wanted to "expose the vulnerability" and "teach a lesson." The lesson was clear: **access control is not a feature you add after testing. It is the default expectation that every state-changing function must satisfy before it can be called secure.**

---

## Why Access Control Breaks

Access control appears simple. A modifier like `onlyOwner` is one line of Solidity. How can one line cause $610 million in losses?

Because access control is not about the modifier. It is about the assumptions that come before it:

1. **Assumption of uniqueness**: The developer assumes the function will only be called by "the right person." They never consider that "the wrong person" might find it.

2. **Assumption of visibility**: The developer assumes internal functions are invisible. In blockchain, every byte of bytecode is public. `private` means "not callable through the ABI"—not "not callable."

3. **Assumption of sequencing**: The developer assumes initialization happens once, at deployment time, in a controlled environment. On-chain, anyone can call any public function at any time.

These assumptions survive because traditional software development teaches them as truths. Access control in a web application means checking a session cookie. If the cookie is missing, the request is rejected. The worst case is a 403 error. In a smart contract, the worst case is PolyNetwork.

---

## Pattern #8: Missing Access Control

**Severity**: HIGH
**Real case**: PolyNetwork $610M

### The Vulnerability

A function performs a privileged operation without verifying that the caller is authorized:

```solidity
// ❌ VULNERABLE: Anyone can upgrade the contract
function upgradeTo(address newImplementation) external {
    _upgradeTo(newImplementation);
    // No onlyOwner. No onlyRole. No require.
    // Anyone who finds this function owns every proxy.
}
```

The function looks correct. It compiles. It does exactly what the name promises. The vulnerability is invisible in the code—it is the absence of something that should be there.

### The Attack

1. Attacker reviews the contract's ABI (publicly visible on Etherscan)
2. Attacker finds a function named `upgradeTo` or `setAdmin` or `changeFee` with no modifier
3. Attacker calls the function with their own address as the parameter
4. The contract executes. The attacker is now the admin.
5. As admin, the attacker upgrades to a malicious implementation or transfers all funds

No flash loan. No oracle manipulation. No reentrancy. Just a function that anyone can call.

### The Fix

```solidity
// ✅ SAFE: Access control via OpenZeppelin Ownable
function upgradeTo(address newImplementation) external onlyOwner {
    _upgradeTo(newImplementation);
}

// Or granular role-based access control:
function upgradeTo(address newImplementation) external onlyRole(UPGRADER_ROLE) {
    _upgradeTo(newImplementation);
}
```

More fundamentally: every state-changing function must have an explicit access control declaration. Linters like Slither flag every external function without a modifier. Treat every flag as a potential PolyNetwork.

---

## Pattern #9: Single Admin Key

**Severity**: HIGH
**Real case**: Ronin Bridge $625M

### The Vulnerability

A protocol's entire security depends on a single private key. If that key is compromised—through phishing, malware, social engineering, or insider threat—the protocol is compromised.

Ronin Bridge used a 5-of-9 validator multi-sig. On paper, this is secure: 5 separate parties must collude. In reality, Sky Mavis controlled 4 of the 9 validators directly and had been delegated authority over a fifth. When the attacker compromised Sky Mavis's infrastructure, they gained control of 5 validators—enough to authorize any withdrawal.

The $625 million loss was not a failure of cryptography. It was a failure of organizational structure. The multi-sig was a single point of failure disguised as distributed trust.

### The Fix

True multi-sig requires organizational diversity:

```solidity
// ❌ VULNERABLE: Multi-sig with centralization
require(signatures.length >= 5);
// Sky Mavis controls 4 validators + 1 delegated = 5 total

// ✅ SAFE: Multi-sig with diversity requirements
require(signatures.length >= 6);
require(uniqueOrganizations(signers) >= 4);  // At least 4 separate orgs
require(uniqueJurisdictions(signers) >= 3);  // At least 3 legal jurisdictions
```

For protocols that cannot achieve organizational diversity, add blast radius limits:

```solidity
uint256 public constant MAX_SINGLE_WITHDRAWAL = 1000 ether;    // Per-tx cap
uint256 public constant DAILY_WITHDRAWAL_LIMIT = 10000 ether;  // 24h cap
uint256 public constant WITHDRAWAL_COOLDOWN = 1 hours;          // Between txns
```

Even if all validators are compromised, the attacker can only drain $10,000 ETH per day. This gives the community time to detect and respond.

---

## Pattern #10: Delegatecall to User-Controlled Address

**Severity**: CRITICAL
**Real case**: Parity Wallet $150M freeze (2017)

### The Vulnerability

`delegatecall` executes another contract's code in the calling contract's context—preserving `msg.sender`, `msg.value`, and, critically, storage access. If the target address is user-supplied, the user can execute arbitrary code that modifies any storage slot.

```solidity
// ❌ VULNERABLE: User controls the delegate target
function execute(address target, bytes calldata data) external {
    (bool success,) = target.delegatecall(data);
    // The target contract can read/write ALL storage of THIS contract
    require(success);
}
```

### The Parity Incident

The Parity multi-sig wallet used a shared library contract as its implementation. An attacker noticed the library was not initialized. They called `initWallet()` on the library—making themselves the owner—then called `kill()` to `selfdestruct` the library.

Every wallet that delegated to this library was now pointing to an address with no code. All wallet functions reverted. $150 million worth of ETH remains frozen in these wallets to this day.

### The Fix

The implementation address must be stored in the contract's own storage and set through a timelocked governance process:

```solidity
// ✅ SAFE: Implementation address in storage, not user-supplied
address public implementation;

function setImplementation(address impl) external onlyGovernance {
    require(block.timestamp >= scheduled[impl], "Timelock not expired");
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

## Pattern #11: Hidden Owner Backdoor

**Severity**: CRITICAL

### The Vulnerability

A protocol advertises "decentralized governance" but retains a single-key emergency function:

```solidity
function emergencyWithdraw(address token) external onlyOwner {
    IERC20(token).transfer(owner, IERC20(token).balanceOf(address(this)));
    // "Emergency" — or backdoor?
}
```

This function exists because the developers are afraid of something going wrong. The irony is that the function itself is the most likely thing to go wrong.

### The Fix

If emergency functions must exist, they must be proportional to the emergency:

```solidity
function emergencyPause() external onlyMultisig {
    // Pause is low-risk: no funds move, just halts operations
    _pause();
}

function emergencyWithdraw(address token, uint256 maxAmount) external onlyGovernance {
    // Withdrawal is high-risk: funds move
    require(maxAmount <= totalValueLocked * 5 / 100, "Max 5%");
    require(block.timestamp >= lastWithdrawal + 7 days, "Weekly limit");
    lastWithdrawal = block.timestamp;
    IERC20(token).transfer(treasury, maxAmount);
}
```

---

## The Access Control Checklist

1. **Every external function has an explicit access modifier.** If Slither flags it, fix it. Do not suppress the warning.
2. **Multi-sig requires organizational diversity.** Not just N-of-M. N-of-M where signers are in different companies, countries, and legal systems.
3. **Upgrade functions have a minimum 48-hour timelock.** No exception. If your protocol needs instant upgrades, your protocol design is wrong.
4. **delegatecall targets are never user-supplied.** The implementation address is stored in contract storage and governed by timelocked multi-sig.
5. **Emergency functions have proportional blast radius.** Pause: low bar. Withdraw funds: very high bar.

---

## Connection to Other Chapters

- **Ch4 (Flash Loans)**: Flash-loaned governance tokens can bypass access control on governance votes. The Beanstalk $182M attack combined flash loans (Ch4, Pattern #6) with governance access control failure (this chapter, Pattern #8).
- **Ch10 (Initialization)**: Unprotected initializers—where anyone can call `initialize()` on an implementation contract—are a specialized form of missing access control. See Ch10, Pattern #21.
- **Ch8 (Cross-Chain)**: Bridge validator centralization (Ronin) is access control failure at the organizational level. See Ch8, Pattern #20.

---

## The Deeper Pattern

Every access control failure in this chapter shares a common thread: the developer assumed the attacker would play by the rules. PolyNetwork assumed nobody would find the unprotected function. Ronin assumed a five-of-nine multi-sig was sufficient. Parity assumed nobody could call `initWallet()` on a library contract.

Security is not about making the rules harder to break. It is about assuming the rules are already broken and building defenses accordingly. If an attacker has your admin key, can they drain the protocol? If an attacker can call any function, which functions destroy value? These are the questions access control must answer—not "how do we stop people from calling this," but "what happens when the wrong person calls this."

The hardening gradient applies here too. Large protocols have faced these failures and lived to tell about them. Small protocols that repeat the same mistakes will not get the same second chance. PolyNetwork recovered because the attacker returned the funds. Ronin recovered because Sky Mavis had the reserves to reimburse users. Your protocol will not have either luxury.

Access control is the foundation. Every other defense in this book—oracle validation, reentrancy guards, flash loan resistance—assumes that the functions these defenses protect are called by authorized users. If access control fails, every other defense is irrelevant.

---

*Next: Chapter 7 — Token Economics Attacks*
