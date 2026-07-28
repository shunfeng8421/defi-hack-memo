# MobileCoin 隐私技术深度分析 — Mixin 生态最独特的技术

**日期**: 2026-07-30
**源码**: /i/mixin-repos/mobilecoin/
**语言**: Rust (no_std + SGX enclave)

---

## 隐私模型全景

MobileCoin 为 Mixin 提供四层隐私保护：

```
┌────────────────────────────────────────────────┐
│ Layer 1: 一次性密钥 (One-time Keys)             │
│   接收方隐私 — 每笔输出有独立公钥                │
│   只有接收方能算出对应私钥                       │
├────────────────────────────────────────────────┤
│ Layer 2: 环签名 (MLSAG Ring Signature)          │
│   发送方隐私 — 真实输入隐藏在环中                │
│   外界无法确定哪个UTXO被花费                     │
├────────────────────────────────────────────────┤
│ Layer 3: Pedersen 承诺 (Confidential Amounts)   │
│   金额隐藏 — v*H + b*G                          │
│   链上只能看到承诺，看不到金额                    │
├────────────────────────────────────────────────┤
│ Layer 4: Bulletproofs 范围证明                   │
│   零知识证明每个金额在 [0, 2^64) 范围内           │
│   防止负数/溢出攻击                              │
└────────────────────────────────────────────────┘
             ↓
     Key Image: x * Hp(x*G)
     双花防护 — 同一密钥只用一次
```

---

## Layer 1: 一次性密钥 (接收方隐私)

### 工作机制

```
接收方生成账户密钥 (a, b):
  a = 私有查看密钥 (view key)
  b = 私有花费密钥 (spend key)
  A = a*G, B = b*G

子地址 i:
  D_i = B + Hs(a | i) * G
  C_i = a * D_i

发送方创建一次性公钥:
  r = 随机数
  onetime_public_key = Hs(r * C_i) * G + D_i
  tx_public_key = r * D_i

接收方恢复私钥:
  onetime_private_key = Hs(a * tx_public_key) + b
  验证: onetime_private_key * G == onetime_public_key
```

**隐私保证**: 链上只看到 `onetime_public_key` 和 `tx_public_key`。第三方无法将这两个值与接收方地址关联——只有持有 `(a, b)` 的接收方能计算对应的私钥。

---

## Layer 2: MLSAG 环签名 (发送方隐私)

### 数学原理

```
给定:
  输入 UTXO 的公钥: P_real (真实)
  诱饵 UTXO 的公钥: P_1, P_2, ..., P_n (环中其他成员)
  对应的 Pedersen 承诺: C_real, C_1, ..., C_n

MLSAG 证明:
  "我知道某个 i 对应的私钥 x_i 和 承诺打开 (v_i, b_i)，
   满足: P_i = x_i * G 且 C_i = v_i * H + b_i * G"

验证者可以验证:
  ✅ 签名有效 — 某个环成员确实签了
  ❌ 但无法确定是哪个环成员
```

**隐私保证**: 每个环成员都有相同的概率是真实发送方。第三方看到签名的概率分布是均匀的——完全匿名。

---

## Layer 3: Pedersen 承诺 (金额隐藏)

```rust
// Pedersen Commitment
pub struct Commitment {
    pub point: RistrettoPoint,  // v*H + b*G
}

fn new(value: u64, blinding: Scalar) -> Self {
    // value 被盲化因子 blinding 隐藏
    Self { point: GENERATORS.commit(Scalar::from(value), blinding) }
}
```

**关键性质**:
- **隐藏性**: 看 `C = v*H + b*G`，无法反推 `v`（没有计算 `b` 的能力）
- **绑定性**: 无法找到另一对 `(v', b')` 满足 `C = v'*H + b'*G`（离散对数假设）
- **同态性**: `C1 + C2 = (v1+v2)*H + (b1+b2)*G` — 输入总和=输出总和可验证

**隐私保证**: 链上只看到椭圆曲线点 `C`。只有持有 `(v, b)` 的发送方和接收方知道真实金额。

---

## Layer 4: Bulletproofs 范围证明

```rust
/// 证明每个秘密值在 [0, 2^64) 范围内
fn prove(values: &[u64], blindings: &[Scalar]) -> RangeProof
```

**为什么需要**: Pedersen 承诺隐藏了金额，但如果不验证范围，攻击者可以创建负金额（通过模运算）：`C(-100) = (2^256 - 100) * H + b * G` 看起来像一个巨大的正金额。

**隐私保证**: 验证者可以确认:
- ✅ 金额在 [0, 2^64) 内 (约 1.8 × 10^19，足够任何合法交易)
- ✅ 不知道具体金额是多少
- ✅ 证明大小仅 ~700 字节（不随输入数量线性增长）

---

## 双花防护: Key Image

```
KeyImage = x * Hp(x * G)

其中:
  x = 私钥
  P = x * G = 公钥
  Hp = 确定性哈希到曲线点
```

**关键性质**: 每个 `(私钥 x, 公钥 P)` 对产生唯一且确定的 `KeyImage`。同一私钥花两次 → 同一个 KeyImage 出现两次 → 双花被检测。

**验证公式**: 验证者不需要知道 `x`，只需要验证环签名中包含 `KeyImage` 的计算正确性。

---

## 交易结构

```rust
Tx {
    prefix: TxPrefix {
        inputs: Vec<TxIn>,        // 引用已有 UTXO (含 Merkle 证明)
        outputs: Vec<TxOut>,       // 新 UTXO (含一次性公钥 + 承诺)
        fee: u64,                  // 手续费 (公开)
    },
    signature: RingMLSAG {         // 整个交易的环签名
        c_zero: CurveScalar,       // 初始挑战值
        responses: Vec<Response>,  // 每层响应
        key_images: Vec<KeyImage>, // 防止双花
    }
}
```

---

## 与 Monero 对比

| 特征 | MobileCoin (Mixin) | Monero |
|------|:--:|:--:|
| 环签名 | MLSAG | CLSAG (更高效) |
| 金额隐藏 | Pedersen (自研) | Pedersen |
| 范围证明 | Bulletproofs | Bulletproofs+ |
| 一次性密钥 | CryptoNote 子地址 | CryptoNote 子地址 |
| 额外特性 | SGX 飞地签名 | 无 TEE |
| 共识 | BFT-DAG (Mixin Kernel) | PoW |

---

## 安全评估

| 组件 | 安全性 | 备注 |
|------|:--:|------|
| 一次性密钥 | ✅ | 数学上安全——等同 Monero |
| 环签名 MLSAG | ✅ | 标准实现, 已验证的密码学 |
| Pedersen 承诺 | ✅ | 隐藏性+绑定性均成立 |
| Bulletproofs | ✅ | 标准实现 |
| Key Image | ✅ | 双花在数学上不可能 |
| SGX 集成 | ⚠️ | 未在 Mixin Kernel 中使用 |

**结论**: MobileCoin 的隐私技术栈是全球最先进的之一——与 Monero 同等级别，加上 SGX 硬件保护。但在 Mixin 的实现中，TEE 组件未被 Kernel 直接使用，隐私保护目前完全依赖密码学而非硬件。这并不削弱隐私——Monero 证明纯密码学隐私已经足够——只是缺失了额外的硬件安全层。
