// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title EVM底层安全 — 存储/升级/预编译漏洞合集
/// @author Shiqiang Chen — 2026

// ═══════════════════════════════════════════
// 漏洞1: UUPS升级存储碰撞
// ═══════════════════════════════════════════
contract UpgradeableV1 {
    uint256 public value;        // slot 0
    address public owner;        // slot 1
    
    function setValue(uint256 v) external { value = v; }
}

/// ⚠️ BUG: V2新增变量挤占了原有布局
contract UpgradeableV2_BUG extends UpgradeableV1 {
    // slot 2 (新增) — 但 UpgradeableV1 的 implementor 可能在slot 2存了东西!
    uint256 public extraData;    // ⚠️ 存储碰撞
    
    function setExtra(uint256 d) external { extraData = d; }
}

/// ✅ FIX: 预留gap
contract UpgradeableV2_FIXED {
    uint256 public value;
    address public owner;
    uint256[50] private __gap;   // ✅ 预留50个slot
    
    uint256 public extraData;    // ✅ 安全 — 实际在 slot 52
}


// ═══════════════════════════════════════════
// 漏洞2: SELFDESTRUCT + CREATE2 碰撞攻击
// ═══════════════════════════════════════════
contract SelfdestructAttack {
    address public target;
    
    /// ⚠️ BUG: 攻击者可:
    /// 1. 部署合约A → 获得地址X
    /// 2. selfdestruct(A)
    /// 3. 用 CREATE2 在相同地址X部署恶意合约B
    /// 4. 合约B有完全不同的逻辑但地址相同
    function attack(bytes32 salt) external {
        new Deployer{salt: salt}();
    }
}

contract Deployer {
    constructor() {
        // 恶意逻辑
    }
}


// ═══════════════════════════════════════════
// 漏洞3: EXTCODESIZE 检查绕过
// ═══════════════════════════════════════════
contract CodeSizeChecker {
    /// ⚠️ BUG: EXTCODESIZE==0 不等于 EOA
    /// 合约在 constructor 执行期间 EXTCODESIZE == 0!
    function isContract(address addr) external view returns (bool) {
        uint256 size;
        assembly { size := extcodesize(addr) }
        return size > 0;
    }
    
    /// ✅ FIX: 检查 tx.origin != msg.sender (不够完美但更好)
    function isContract_FIXED(address addr) external view returns (bool) {
        return addr != tx.origin; // or check codehash
    }
}


// ═══════════════════════════════════════════
// 漏洞4: ecrecover 预编译 — 返回0地址不抛出
// ═══════════════════════════════════════════
/// @dev ecrecover(hash, v, r, s) 对无效签名返回 address(0)，不revert!
contract EcrecoverAttacker {
    function bypassAuth(
        bytes32 hash, bytes memory fakeSig
    ) external view returns (bool) {
        (uint8 v, bytes32 r, bytes32 s) = abi.decode(fakeSig, (uint8, bytes32, bytes32));
        address signer = ecrecover(hash, v, r, s);
        // ⚠️ 攻击者可以构造 v,r,s 使 ecrecover 返回 0
        // 如果 owner 初始化时误设为 address(0)...
        return signer != address(0); // 无效签名不一定是恶意
    }
}


// ═══════════════════════════════════════════
// 漏洞5: Gas Griefing — 循环中无gas限制
// ═══════════════════════════════════════════
contract GasGriefing {
    address[] public users;
    
    /// ⚠️ BUG: 循环长度完全由用户控制 → OOG
    function bulkTransfer(uint256[] calldata amounts) external payable {
        for (uint256 i = 0; i < amounts.length; i++) {
            (bool ok,) = users[i].call{value: amounts[i]}("");
            // ⚠️ 如果 users.length = 10000 → 必定 OOG，ETH锁死
        }
    }
    
    /// ✅ FIX: 分批处理
    function bulkTransfer_FIXED(uint256 start, uint256 end, uint256[] calldata amounts) external {
        require(end - start <= 50, "max batch 50");
        for (uint256 i = start; i < end; i++) {
            (bool ok,) = users[i].call{value: amounts[i]}("");
        }
    }
}


// ═══════════════════════════════════════════
// 漏洞6: 预编译 ModExp — 输入可控导致无限gas
// ═══════════════════════════════════════════
contract ModExpGriefing {
    /// ⚠️ BUG: 用户提供 BASE/EXP/MOD 的字节长度
    function modExp(
        bytes calldata base, bytes calldata exp, bytes calldata mod
    ) external view returns (bytes memory) {
        uint256 inputLen = base.length + exp.length + mod.length;
        // 如果 exp 是 4096字节 → gas = inputLen^3 数量级 → OOG
        // ModExp 定价 = max(mult_complexity, floor(mult_complexity * iter_count / 20))
        // 但 iter_count 完全由用户控制!
        assembly {
            let result := staticcall(gas(), 0x05, add(base.offset, 0x20), inputLen, 0, 0)
        }
    }
}

/// ============================================================
/// EVM底层安全 — 6大漏洞类
/// 1. 存储碰撞 (upgrade + DELEGATECALL)
/// 2. CREATE2 + SELFDESTRUCT 地址碰撞
/// 3. EXTCODESIZE 绕过 (constructor期间)
/// 4. ecrecover 返回0地址
/// 5. Gas griefing (用户控制循环)
/// 6. 预编译 ModExp gas燃烧
/// ============================================================
