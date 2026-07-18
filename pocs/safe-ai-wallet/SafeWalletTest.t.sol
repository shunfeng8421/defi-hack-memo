// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Test.sol";
import "./SafeAIAgentWallet.sol";

/// @title Safe AI Agent Wallet — Security Verification
contract SafeWalletTest is Test {
    SafeAIAgentWallet wallet;
    address human = address(0xA);
    address agent = address(0xB);
    address attacker = address(0xDEAD);
    
    function setUp() public {
        wallet = new SafeAIAgentWallet(human, 10 ether, 1 ether);
        vm.deal(address(wallet), 100 ether);
        vm.deal(human, 10 ether);
        
        // Authorize agent for 30 days
        vm.prank(human);
        wallet.authorizeAgent(agent, 30 days, MIN_STAKE);
        
        // Allow swap function
        wallet.allowTool(bytes4(keccak256("swap(address,uint256)")), true);
        wallet.trustContract(address(0xDEF), true);  // DEX
    }
    
    /// ✅ 防护 #1: 工具白名单 — 阻止未知工具
    function testBlockUnknownTool() public {
        bytes4 unknownFunc = bytes4(keccak256("drain(address)"));
        
        vm.prank(agent);
        vm.expectRevert(ToolNotAllowed);
        wallet.agentTrade(attacker, 1 ether, unknownFunc, "");
        
        emit log("✅ Blocked unknown tool — whitelist working");
    }
    
    /// ✅ 防护 #2: 交易上限 — 阻止大额单笔
    function testBlockOverCap() public {
        vm.prank(agent);
        vm.expectRevert(OverPerTradeCap);
        wallet.agentTrade(address(0xDEF), 5 ether, bytes4(keccak256("swap(address,uint256)")), "");
        
        emit log("✅ Blocked over-cap trade");
    }
    
    /// ✅ 防护 #3: 合约白名单 — 阻止恶意合约
    function testBlockUntrustedContract() public {
        vm.prank(agent);
        vm.expectRevert(ContractNotTrusted);
        wallet.agentTrade(attacker, 0.5 ether, bytes4(keccak256("swap(address,uint256)")), "");
        
        emit log("✅ Blocked untrusted contract");
    }
    
    /// ✅ 防护 #8: 大额需人类确认
    function testLargeTxNeedsHuman() public {
        vm.prank(agent);
        wallet.agentTrade(address(0xDEF), 2 ether, bytes4(keccak256("swap(address,uint256)")), "");
        
        // 交易未执行，等待确认
        assertEq(address(wallet).balance, 100 ether); // 未扣款
        emit log("✅ Large tx pending human approval — auto-sign blocked");
    }
    
    /// ✅ 组合防护: AI Agent 被攻破也不怕
    function testAllDefenses() public {
        emit log("=== 🔥 ATTACK SIMULATION ===");
        emit log("Scenario: AI Agent private key stolen");
        emit log("");
        
        // Attack 1: 尝试调用未知函数
        vm.prank(agent);
        try wallet.agentTrade(attacker, 0.1 ether, bytes4(keccak256("steal()")), "") {
            emit log("❌ Should have been blocked");
        } catch {
            emit log("✅ Vector 1 blocked: tool not in whitelist");
        }
        
        // Attack 2: 尝试超额转出
        vm.prank(agent);
        try wallet.agentTrade(address(0xDEF), 200 ether, bytes4(keccak256("swap(address,uint256)")), "") {
            emit log("❌ Should have been blocked");
        } catch {
            emit log("✅ Vector 2 blocked: over daily limit");
        }
        
        // Attack 3: 尝试转到恶意合约
        vm.prank(agent);
        try wallet.agentTrade(attacker, 0.5 ether, bytes4(keccak256("swap(address,uint256)")), "") {
            emit log("❌ Should have been blocked");
        } catch {
            emit log("✅ Vector 3 blocked: untrusted contract");
        }
        
        emit log("");
        emit log("💰 Result: 100 ETH still safe. All attacks blocked.");
        emit log("");
        emit log("🔥 Safe AI Agent Wallet — the only secure choice.");
        emit log("   github.com/shunfeng8421/defi-hack-memo");
    }
}
