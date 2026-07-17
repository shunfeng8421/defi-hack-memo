// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Test.sol";
import "../vulnerable/MinimalBridge.sol";
import "../fixed/FixedBridge.sol";

/// @title 跨链桥全部漏洞验证
contract BridgeExploitTest is Test {
    MinimalBridge public badBridge;
    FixedBridge public goodBridge;
    address validator;
    uint256 validatorKey;
    address attacker;

    function setUp() public {
        (validator, validatorKey) = makeAddrAndKey("validator");
        attacker = makeAddr("attacker");
        badBridge = new MinimalBridge(validator);
        goodBridge = new FixedBridge(validator);
        vm.deal(address(badBridge), 100 ether);
        vm.deal(address(goodBridge), 100 ether);
    }

    /// @notice 漏洞1: 签名重放 — 同一签名无限提款
    function testSignatureReplay() public {
        // Validator signs one withdrawal
        bytes32 message = keccak256(abi.encodePacked(attacker, uint256(1 ether), bytes32(0)));
        bytes32 digest = keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", message));
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(validatorKey, digest);
        bytes memory sig = abi.encodePacked(r, s, v);

        // First withdraw — works
        badBridge.withdraw(attacker, 1 ether, bytes32(0), sig);
        
        // Second withdraw with SAME signature — also works (replay!)
        vm.expectRevert(); // should revert but doesn't
        badBridge.withdraw(attacker, 1 ether, bytes32(0), sig);
        // ⚠️ 验证失败 — 没有nonce所以重放成功
    }

    /// @notice 漏洞2: 跨链重放 — chainId不匹配
    function testCrossChainReplay() public {
        // 在chainId=31337签的名，在chainId=1同样有效
        // badBridge没有chainId保护
    }

    /// @notice 修复版: nonce防止重放
    function testFixedNonce() public {
        bytes32 structHash = keccak256(abi.encode(
            keccak256("Withdraw(address user,uint256 amount,bytes32 sourceTx,uint256 nonce,uint256 deadline)"),
            attacker, uint256(1 ether), bytes32(0), uint256(0), uint256(block.timestamp + 1 days)
        ));
        bytes32 digest = goodBridge._hashTypedDataV4(structHash);
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(validatorKey, digest);
        bytes memory sig = abi.encodePacked(r, s, v);

        goodBridge.withdraw(attacker, 1 ether, bytes32(0), 0, block.timestamp + 1 days, sig);
        
        // 第二次用相同nonce → 应该失败
        vm.expectRevert("nonce used");
        goodBridge.withdraw(attacker, 1 ether, bytes32(0), 0, block.timestamp + 1 days, sig);
    }
}
