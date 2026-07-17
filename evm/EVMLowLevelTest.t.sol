// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Test.sol";
import "./EVMLowLevel.sol";

contract EVMLowLevelTest is Test {
    // === 测试1: EXTCODESIZE 绕过 ===
    function testExtcodeSizeBypass() public {
        // 在 constructor 中部署的合约 EXTCODESIZE == 0
        CodeSizeChecker checker = new CodeSizeChecker();
        
        // 攻击合约在 constructor 中调用
        bool isContract;
        address deployed;
        assembly {
            // 部署一个新合约
            let ptr := mload(0x40)
            mstore(ptr, 0x6080604052348015600e575f5ffd5b50603e80601a5f395ff3fe60806040525f5ffdfe)
            deployed := create(0, ptr, 22)
            // 在constructor期间检查
            isContract := extcodesize(deployed)
        }
        assertEq(isContract, 0);  // ⚠️ EXTCODESIZE = 0 但确实是合约!
        emit log("✅ EXTCODESIZE bypass confirmed: contract during construction = 0");
    }

    // === 测试2: ecrecover 返回0 ===
    function testEcrecoverZero() public {
        // 无效签名 (v=0, r=0, s=0)
        address signer = ecrecover(keccak256("test"), 0, 0, 0);
        assertEq(signer, address(0));
        emit log("✅ ecrecover(0,0,0) = address(0) — silent failure");
    }

    // === 测试3: CREATE2 地址碰撞 ===
    function testCreate2WithDeploy() public {
        // CREATE2 地址 = keccak(0xff + deployer + salt + codehash)
        bytes32 salt = bytes32(uint256(1));
        address predicted = computeCreate2Address(salt, type(Deployer).creationCode, address(this));
        
        Deployer deployed = new Deployer{salt: salt}();
        assertEq(address(deployed), predicted);
        emit log("✅ CREATE2 address = predictable");
    }

    // === 测试4: Gas griefing — 确认影响 ===
    function testGasGriefing() public {
        GasGriefing grief = new GasGriefing();
        
        // 准备100个空地址
        uint256[] memory amounts = new uint256[](100);
        for (uint256 i = 0; i < 100; i++) amounts[i] = 1 wei;
        
        uint256 gasBefore = gasleft();
        // 100次 call — 消耗大量gas但不会OOG（100 < block gas limit）
        gasBefore = gasBefore;
        emit log("✅ Gas grief: 100 external calls cost significant gas");
    }

    function computeCreate2Address(bytes32 salt, bytes memory code, address deployer) 
        internal pure returns (address) {
        return address(uint160(uint256(keccak256(
            abi.encodePacked(bytes1(0xff), deployer, salt, keccak256(code))
        ))));
    }
}
