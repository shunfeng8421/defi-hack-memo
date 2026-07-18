// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/// @title MinimalCrossChainBridge — FIXED VERSION
/// @dev 修复了4个漏洞
contract FixedBridge is EIP712, ReentrancyGuard {
    bytes32 private constant WITHDRAW_TYPEHASH = 
        keccak256("Withdraw(address user,uint256 amount,bytes32 sourceTx,uint256 nonce,uint256 deadline)");
    
    mapping(address => uint256) public balances;
    mapping(uint256 => bool) public usedNonces;
    address public validator;
    uint256 public constant TIMELOCK = 2 days;
    uint256 public emergencyTimelock;
    address public pendingValidator;

    event Withdrawn(address user, uint256 amount, bytes32 sourceTx, uint256 nonce);

    constructor(address _validator) EIP712("MinimalBridge", "1") {
        validator = _validator;
    }

    /// @notice 存款
    function deposit(bytes32 destAddr) external payable {
        require(msg.value > 0, "zero");
        balances[msg.sender] += msg.value;
    }

    /// @notice ✅ 修复: EIP-712 + nonce + deadline + chainId
    function withdraw(
        address user, uint256 amount, bytes32 sourceTx,
        uint256 nonce, uint256 deadline, bytes calldata signature
    ) external nonReentrant {
        require(block.timestamp <= deadline, "expired");        // ✅ BUG 3 fixed
        require(!usedNonces[nonce], "nonce used");              // ✅ BUG 1 fixed
        usedNonces[nonce] = true;

        bytes32 structHash = keccak256(
            abi.encode(WITHDRAW_TYPEHASH, user, amount, sourceTx, nonce, deadline)
        );
        bytes32 digest = _hashTypedDataV4(structHash);          // ✅ BUG 2 fixed (domain includes chainId)
        address signer = ECDSA.recover(digest, signature);
        require(signer == validator, "bad sig");

        // ✅ BUG 4 fixed: CEI pattern
        balances[user] -= amount;
        (bool ok,) = user.call{value: amount}("");
        require(ok, "transfer failed");
        
        emit Withdrawn(user, amount, sourceTx, nonce);
    }

    /// @notice ✅ 修复: 时间锁 + 两步转移
    function proposeTransferValidator(address newValidator) external {
        require(msg.sender == validator, "only validator");
        pendingValidator = newValidator;
        emergencyTimelock = block.timestamp + TIMELOCK;
    }

    function acceptValidator() external {
        require(msg.sender == pendingValidator, "not pending");
        require(block.timestamp >= emergencyTimelock, "timelock");
        validator = pendingValidator;
        pendingValidator = address(0);
    }
}
