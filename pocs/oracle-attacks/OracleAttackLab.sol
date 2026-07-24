// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Oracle Manipulation Lab — 10 Attack Vectors
/// @notice Each attack is a standalone demo contract showing the vulnerability
/// @author Shiqiang Chen · July 2026

// ============================================================
// #1: Spot Price Oracle (Uniswap V2)
// ============================================================
contract Attack1_SpotPrice {
    IUniswapV2Pair pair;
    
    function exploit() external {
        // VULNERABLE: Uses getReserves() for price
        (uint256 reserve0, uint256 reserve1,) = pair.getReserves();
        uint256 price = reserve0 * 1e18 / reserve1; // Spot price — manipulable!
        
        // Attack: flash loan → swap → manipulate reserves → call protocol with fake price
    }
    
    function safe() external view returns (uint256) {
        // FIX: Use TWAP oracle
        return pair.price0CumulativeLast(); // Cumulative price, not spot
    }
}

// ============================================================
// #2: TWAP Manipulation via Multi-Block Attack
// ============================================================
contract Attack2_TWAPMultiBlock {
    // Even TWAP can be manipulated across multiple blocks
    // Attack: control block N-1 → manipulate price → block N reads fake TWAP
    // Requires validator collusion or mempool manipulation
}

// ============================================================
// #3: Chainlink Stale Price
// ============================================================
contract Attack3_ChainlinkStale {
    AggregatorV3Interface public priceFeed;
    
    function exploit() external view returns (int256) {
        (, int256 price,,,) = priceFeed.latestRoundData();
        return price; // VULNERABLE: No staleness check!
        // Attack: wait for oracle to stop updating → use stale price
    }
    
    function safe() external view returns (int256) {
        (, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();
        require(block.timestamp - updatedAt < 1 hours, "Stale price");
        return price;
    }
}

// ============================================================
// #4: Self-Reported Oracle
// ============================================================
contract Attack4_SelfReported {
    uint256 public price; // VULNERABLE: Anyone can set this!
    
    function setPrice(uint256 _price) external {
        price = _price; // No access control, no TWAP, no validation
    }
    
    // Attack: set price to 0 → liquidate everyone → profit
}

// ============================================================
// #5: LP Token as Collateral
// ============================================================
contract Attack5_LPTokenCollateral {
    // VULNERABLE: Uses LP token price = pool value / totalSupply
    // Attack: flash loan → add liquidity → inflate LP token price → borrow against inflated collateral
}

// ============================================================
// #6: Curve Pool Oracle
// ============================================================
contract Attack6_CurveOracle {
    ICurvePool public pool;
    
    function exploit() external view returns (uint256) {
        return pool.get_virtual_price(); // VULNERABLE: Virtual price can be manipulated via flash loan
    }
}

// ============================================================
// #7: Balancer Weighted Pool Oracle
// ============================================================
contract Attack7_BalancerOracle {
    IBalancerVault public vault;
    bytes32 public poolId;
    
    function exploit() external view returns (uint256) {
        // VULNERABLE: getSpotPrice() returns instantaneous price
        // Attack: flash loan imbalance → spot price goes to 0 → protocol thinks collateral = $0
    }
}

// ============================================================
// #8: Multi-Hop Oracle Manipulation
// ============================================================
contract Attack8_MultiHop {
    // VULNERABLE: Oracle uses tokenA → tokenB → tokenC path
    // Attack: manipulate tokenB price → both A and C prices affected
    // Amplification: small capital → large oracle error
}

// ============================================================
// #9: Admin Updatable Oracle
// ============================================================
contract Attack9_AdminOracle {
    address public admin;
    uint256 public lastPrice;
    
    // VULNERABLE: Admin can set arbitrary price with instant effect
    function updatePrice(uint256 _price) external {
        require(msg.sender == admin, "!admin");
        lastPrice = _price; // No delay, no bounds, no TWAP
    }
    
    // FIX: Add timelock + deviation bounds
    function safeUpdate(uint256 _price) external {
        require(msg.sender == admin, "!admin");
        require(_price < lastPrice * 12 / 10, ">10% up"); // Max 10% change
        require(_price > lastPrice * 8 / 10, ">10% down");
        priceTimelock[block.timestamp + 24 hours] = _price;
    }
    mapping(uint256 => uint256) public priceTimelock;
}

// ============================================================
// #10: Delayed Oracle + Flash Loan
// ============================================================
contract Attack10_DelayedOracle {
    // VULNERABLE: Protocol reads price, then waits T blocks, then acts on it
    // Attack: 
    //   1. Flash loan at block N
    //   2. Manipulate price
    //   3. Protocol reads fake price at block N
    //   4. Protocol acts at block N+T using block N's price
    //   5. Attacker already unwound position
}

// ============================================================
// Interfaces
// ============================================================
interface IUniswapV2Pair {
    function getReserves() external view returns (uint256, uint256, uint32);
    function price0CumulativeLast() external view returns (uint256);
}

interface AggregatorV3Interface {
    function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80);
}

interface ICurvePool {
    function get_virtual_price() external view returns (uint256);
}

interface IBalancerVault {
    function getPoolTokens(bytes32) external view returns (address[], uint256[], uint256);
}

/// @title Oracle Attack Summary
/// @dev Run all 10 demos to understand each attack vector
contract OracleAttackLab {
    // Each contract above demonstrates one attack
    // Real implementations would include Foundry test files
    // See: pocs/oracle-attacks/OracleAttackLab.t.sol
}
