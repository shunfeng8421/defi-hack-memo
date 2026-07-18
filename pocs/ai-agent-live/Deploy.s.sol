// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Script.sol";
import "./AIAgentLive.sol";

/// @title Deploy AI Agent Wallet to Base Sepolia
contract DeployAIAgent is Script {
    function run() external {
        vm.startBroadcast();
        
        MockDEX dex = new MockDEX();
        MockLending lending = new MockLending();
        AgentMemory memory_contract = new AgentMemory();
        
        AIAgentWallet wallet = new AIAgentWallet(
            address(dex),
            address(lending),
            address(memory_contract)
        );
        
        vm.deal(address(wallet), 100 ether);
        
        console.log("DEX:", address(dex));
        console.log("Lending:", address(lending));
        console.log("Memory:", address(memory_contract));
        console.log("Wallet:", address(wallet));
        console.log("Deployer:", msg.sender);
        console.log("");
        console.log("🔥 AI Agent Wallet deployed. Come hack it.");
        
        vm.stopBroadcast();
    }
}
