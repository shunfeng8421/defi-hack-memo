// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title ZK Proof Verification — 教学用
/// @dev 演示 ZK 证明验证中的常见错误
/// @author Shiqiang Chen — 2026

/// 简化版 ZK 验证器 (模拟 Groth16)
contract SimpleZKVerifier {
    // ⚠️ BUG 1: 硬编码验证密钥 — 无法升级
    bytes32 public constant VK_ALPHA = bytes32(uint256(1));
    
    mapping(bytes32 => bool) public verifiedProofs;
    
    /// 验证 Groth16 证明 (极度简化)
    function verifyProof(
        uint256[2] calldata a,      // proof.a (G1)
        uint256[2][2] calldata b,   // proof.b (G2)
        uint256[2] calldata c,      // proof.c (G1)
        uint256[2] calldata input   // public inputs
    ) external view returns (bool) {
        // 真实场景: 椭圆曲线配对验证
        // e(A, B) == e(Alpha, Beta) * e(C, Delta) * e(input, Gamma)
        
        // ⚠️ BUG 2: 简化配对 — 不验证配对是否相等
        uint256 lhs = a[0] + b[0][0] + c[0]; // 这不是真实配对!
        uint256 rhs = input[0] + input[1];
        return lhs >= rhs; // ⚠️ 宽松验证 — 可绕过
    }
    
    /// ⚠️ BUG 3: 缺少防重放
    function processWithdrawal(
        address user, uint256 amount,
        uint256[2] calldata a,
        uint256[2][2] calldata b,
        uint256[2] calldata c,
        uint256[2] calldata input
    ) external {
        require(verifyProof(a, b, c, input), "invalid proof");
        // ⚠️ 同一证明可重复使用 — 无限提款
        (bool ok,) = user.call{value: amount}("");
        require(ok);
    }
}

/// ============================================================
/// ZK 漏洞分类 (与我们 Aztec $2.19M 分析对应)
/// ============================================================
/// 1. 配对验证不完整 — 允许伪造证明
/// 2. 无 proof id/hash — 证明可重放 (Aztec 类似)
/// 3. 硬编码 VK — 无法升级
/// 4. 无 `numRealTxs` 检查 — 证明覆盖范围 > 实际执行范围 (Aztec 根因)
/// 5. 公共输入未完全覆盖状态转换
