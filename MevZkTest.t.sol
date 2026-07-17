// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Test.sol";
import "./SimpleAMM.sol";
import "../zk/SimpleZKVerifier.sol";

contract MevZkTest is Test {
    // === MEV Sandwich Test ===
    function testSandwichAttack() public {
        SimpleAMM amm = new SimpleAMM(100 ether, 100 ether); // 100 TOKEN : 100 ETH
        MevSandwichBot bot = new MevSandwichBot(amm);
        
        // Price before: 1 TOKEN = 1 ETH
        uint256 priceBefore = amm.getTokenPrice();
        assertEq(priceBefore, 1e18);
        
        // Attacker front-runs with 10 ETH → buys TOKEN
        vm.deal(address(bot), 50 ether);
        uint256 profit = bot.sandwich(10 ether, 10 ether);
        
        // Price after manipulation ≠ original
        uint256 priceAfter = amm.getTokenPrice();
        assert(priceAfter != priceBefore);
        emit log("✅ MEV sandwich: price moved by front-run");
    }

    // === ZK Proof Replay Test ===
    function testZkProofReplay() public {
        SimpleZKVerifier verifier = new SimpleZKVerifier();
        
        uint256[2] memory a = [uint256(5), 0];
        uint256[2][2] memory b = [[uint256(3), 0], [uint256(0), 0]];
        uint256[2] memory c = [uint256(3), 0];
        uint256[2] memory input = [uint256(2), 2];
        
        // First verification — passes
        bool first = verifier.verifyProof(a, b, c, input);
        assertTrue(first);
        
        // Same proof used again — still passes (replay!)
        bool second = verifier.verifyProof(a, b, c, input);
        assertTrue(second);
        emit log("✅ ZK proof replay: same proof verified twice");
    }
}
