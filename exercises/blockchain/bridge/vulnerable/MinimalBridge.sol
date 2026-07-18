// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title MinimalCrossChainBridge — 教学用最简跨链桥
/// @dev BUG VERSION — 故意包含跨链桥最常见的4个漏洞
/// @author Shiqiang Chen — 2026

contract MinimalBridge {
    mapping(address => uint256) public balances;
    // ⚠️ BUG 1: 无 nonce — 签名可重放
    // ⚠️ BUG 2: 无 chainId — 跨链重放
    // ⚠️ BUG 3: 无 deadline — 永不过期
    address public validator;
    
    event Deposited(address indexed user, uint256 amount, bytes32 destAddr);
    event Withdrawn(address indexed user, uint256 amount, bytes32 sourceTx);
    event EmergencyWithdraw(address indexed admin, uint256 amount);

    constructor(address _validator) {
        validator = _validator;
    }

    /// @notice 源链：用户存入资金，获得验证者签名
    function deposit(bytes32 destAddr) external payable {
        require(msg.value > 0, "zero deposit");
        balances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value, destAddr);
    }

    /// @notice 目标链：验证者签名后提款
    /// @dev BUG: 签名无 nonce/chainId/deadline
    function withdraw(
        address user,
        uint256 amount,
        bytes32 sourceTx,
        bytes calldata signature
    ) external {
        // ⚠️ 所有4个bug都在这里
        bytes32 message = keccak256(abi.encodePacked(user, amount, sourceTx));
        bytes32 ethSigned = keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", message));
        
        address signer = recoverSigner(ethSigned, signature);
        require(signer == validator, "invalid signature");

        require(address(this).balance >= amount, "insufficient");
        balances[user] -= amount;  // ⚠️ BUG 4: CEI — 先减后转，但transfer可能重入
        (bool ok,) = user.call{value: amount}("");
        require(ok, "transfer failed");
        
        emit Withdrawn(user, amount, sourceTx);
    }

    /// @notice ⚠️ BUG: 管理员紧急提款 — 无时间锁
    function emergencyWithdraw(address to, uint256 amount) external {
        require(msg.sender == validator, "only validator");
        (bool ok,) = to.call{value: amount}("");
        require(ok);
    }

    function recoverSigner(bytes32 hash, bytes memory sig) internal pure returns (address) {
        require(sig.length == 65, "invalid sig");
        bytes32 r; bytes32 s; uint8 v;
        assembly {
            r := mload(add(sig, 32))
            s := mload(add(sig, 64))
            v := byte(0, mload(add(sig, 96)))
        }
        if (v < 27) v += 27;
        return ecrecover(hash, v, r, s);
    }
}
