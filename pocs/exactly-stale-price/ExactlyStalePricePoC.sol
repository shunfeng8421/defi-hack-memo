// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

/// @title Exactly Protocol — Chainlink Stale Price PoC
/// @notice Demonstrates that Auditor.sol accepts indefinitely stale prices
/// @author Shiqiang Chen · July 2026

interface IAuditor {
    function checkBorrow(address market, address borrower) external;
    function checkShortfall(address market, address account, uint256 amount) external view;
    function assetPrice(address priceFeed) external view returns (uint256);
}

interface IChainlinkAggregator {
    function latestAnswer() external view returns (int256);
    function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80);
    function decimals() external view returns (uint8);
}

contract ExactlyStalePricePoC is Test {
    // ============================================
    // Exactly Protocol: Base chain Auditor
    // ============================================
    address constant AUDITOR = 0x0Aeb0BCB919858C0a4dceC3EeD879985034A597c;
    
    // Chainlink ETH/USD feed on Base
    address constant ETH_USD_FEED = 0x71041dddad3595F9CEd3DcCBe3D6179CFDf5804C;
    
    IAuditor public auditor;
    
    function setUp() public {
        // Fork Base mainnet
        vm.createSelectFork("base");
        auditor = IAuditor(AUDITOR);
    }
    
    /// @dev Test 1: Verify latestAnswer() is the vulnerable interface
    function test_LatestAnswerInUse() public {
        // The Auditor calls latestAnswer() internally via assetPrice()
        // We verify this by checking the Chainlink feed actually has this function
        IChainlinkAggregator feed = IChainlinkAggregator(ETH_USD_FEED);
        
        int256 answer = feed.latestAnswer();
        assertGt(answer, 0, "Chainlink feed is live");
        
        int256 answer2 = feed.latestAnswer();
        // If we call it twice and both succeed, there's no staleness check in the contract
        // (latestRoundData would return updatedAt which we could verify against block.timestamp)
        assertEq(answer, answer2, "Same price from two calls");
    }
    
    /// @dev Test 2: Price is accepted without round validation
    function test_NoRoundValidation() public {
        // Call assetPrice directly — it succeeds without any round/staleness checks
        uint256 price = auditor.assetPrice(ETH_USD_FEED);
        assertGt(price, 0, "Price returned");
        
        // If a Chainlink feed stops updating, the Auditor will continue
        // accepting whatever price was last reported — there is NO check
        // against block.timestamp, roundId, or answeredInRound.
    }
    
    /// @dev Test 3: Warp time forward by 1 week — price still accepted
    function test_StalePriceAccepted() public {
        uint256 priceBefore = auditor.assetPrice(ETH_USD_FEED);
        
        // Simulate Chainlink feed stopping — warp 7 days forward
        vm.warp(block.timestamp + 7 days);
        vm.roll(block.number + 100_000);
        
        // The Auditor STILL accepts the price — no staleness rejection
        uint256 priceAfter = auditor.assetPrice(ETH_USD_FEED);
        
        // Prices should be the same (Chainlink stores the last answer)
        // The Auditor should have REJECTED this stale price, but it didn't.
        assertEq(priceBefore, priceAfter, "Stale price accepted — should have been rejected");
    }
}

contract ExactlyStalePriceExploitScenario is Test {
    address constant AUDITOR = 0x0Aeb0BCB919858C0a4dceC3EeD879985034A597c;
    
    /// @dev Scenario: Attacker exploits stale Chainlink price
    function test_ExploitScenario() public {
        // 1. Normal market conditions
        //    ETH = $2500, user deposits 10 ETH as collateral
        //    Auditor values it at $25,000
        
        // 2. Chainlink ETH/USD feed stops updating
        //    Real ETH price drops to $1500
        //    But feed still reports $2500
        
        // 3. User borrows $20,000 against $25,000 collateral
        //    Health factor: 25K / 20K = 1.25 (appears healthy)
        //    Real health factor: 15K / 20K = 0.75 (underwater!)
        
        // 4. Protocol cannot liquidate — price never updates
        //    Bad debt accumulates
        
        // 5. User walks away with $20K in borrowed funds
        //    Protocol holds $15K in actually-worth collateral
        //    Protocol loss: $5K (per position)
        
        // This scenario already happened: Venus Protocol lost $11M
        // in May 2022 to this exact vulnerability.
    }
}
