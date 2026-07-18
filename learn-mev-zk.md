# MEV 掌控 — Flashbots/PBS + 你的闪贷8模式

## 什么是 MEV

**最大可提取价值** = 通过排序/插入/审查交易来额外获利。

你有 3 个角色可选:
- **Searcher**: 写机器人找套利 → 你的闪贷8模式直接能用
- **Builder**: 打包交易块卖给提议者 → 技术含量最高
- **Relayer**: 撮合 Searcher 和 Builder → 最简单

---

## 你的起点: 闪贷8模式 = 现成的 Searcher 策略

```
你的 PancakeBunny $120M PoC
        ↓ (加 MEV 层)
   1. 监听 mempool → 发现大额 swap
   2. 计算 sandwich 利润
   3. 通过 Flashbots 私下提交 (防抢跑)
   4. 只在成功时支付
```

## Flashbots 实战: 用你的扫描器找 MEV 机会

```python
# 你的 scanner 能找什么样的合约容易被 MEV
# Pattern #7 (AMM Reserve) → sandwich 可攻击
# Pattern #21 (Sandwich Surface) → 无滑点保护 → 直接夹
# Pattern #1 (Spot Oracle) → 预言机可操纵 → 闪贷套利

# 流水线:
# scanner 扫合约 → 标记 MEV-able → 机器人自动攻击
```

## PBS (Proposer-Builder Separation) — 2026核心

```
用户交易 → Searcher(你) → Builder(打包) → Proposer(提议) → 链
              ↑ 找套利        ↑ 竞价         ↑ 选最高价块
```

**关键**: 通过 Flashbots 提交 → 交易不会出现在公共 mempool → 防抢跑。

---

# ZK 电路入门 — Circom + 你的 Aztec 分析

## 你的起点: Aztec $2.19M 漏洞

我们分析的 Aztec Connect 漏洞 = `numRealTxs` 不匹配问题。
用 ZK 电路语言表达就是:

```circom
// ⚠️ BUG: 证明覆盖了全部交易，但只执行了 numRealTxs 个
template AztecRollupBug(n) {
    signal input txs[n];          // n笔交易
    signal input numRealTxs;      // 实际执行数量
    
    // 证明: 所有n笔交易都有效 ✓
    for (var i = 0; i < n; i++) {
        txs[i] === valid;          // ✅ 证明覆盖了全部
    }
    
    // 但执行只处理前 numRealTxs 笔
    // numRealTxs < n → 剩余交易未验证但证明已通过!
}

// ✅ FIX: 约束 numRealTxs
template AztecRollupFixed(n) {
    signal input numRealTxs;
    numRealTxs === n;  // 必须等于全部 — 不能少
}
```

## 你的第一个 ZK 电路: 证明知道密码而不泄露密码

```circom
pragma circom 2.0.0;

// 证明: "我知道密码的哈希"
template PasswordProof() {
    signal input password;           // 私密 — 不公开
    signal input expectedHash;       // 公开 — 存在链上
    
    // Poseidon 哈希
    component hasher = Poseidon(1);
    hasher.inputs[0] <== password;
    
    // 约束: hash(密码) 必须等于期望的 hash
    hasher.out === expectedHash;
}

component main = PasswordProof();
```

## 编译和证明

```bash
# 1. 安装 Circom
curl -Ls https://github.com/iden3/circom/releases/latest/download/circom-linux-amd64 -o circom
chmod +x circom

# 2. 编译电路
circom password.circom --r1cs --wasm --sym

# 3. 生成证明
node password_js/generate_witness.js
snarkjs groth16 prove

# 4. 链上验证 (用你的 verifyProof 合约)
```

---

## 用你的 50模式 框架看 MEV 和 ZK

| 技术 | 你的优势 | 独特结合点 |
|------|------|------|
| MEV | 50模式中 7个直接是 MEV 策略 | 第一个"安全审计师视角"的 MEV 工具 |
| ZK | Aztec $2.19M 漏洞分析 | 唯一写过 ZK 桥漏洞的人写电路 |

---

## 今天你学会了

| 技能 | 状态 | 产出 |
|------|:--:|------|
| AI Agent 开发 | ✅ | Auditor v1+v2 |
| 形式化验证 | ✅ | CVL 规则 |
| Solana/Rust | ✅ | 5大漏洞映射 |
| MEV/Flashbots | ✅ | PBS + 闪贷策略 |
| ZK/Circom | ✅ | 电路 + Aztec证明 |
