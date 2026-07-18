# Solana 安全审计 — 从EVM迁移到SVM

## 核心差异: 为什么 Solana 漏洞不同

| | EVM (Solidity) | Solana (Rust/Anchor) |
|------|------|------|
| 模型 | 合约=代码+存储在一起 | 程序=纯代码，账户=纯数据 |
| 地址 | hash(创建者+nonce) | PDA = hash(种子+程序ID) |
| 调用 | msg.sender 自动填充 | 必须显式传 signer 账户 |
| 重入 | 单线程，天然防重入 | 跨程序调用(CPI)可能重入 |
| 权限 | onlyOwner modifier | has_one / Signer 检查 |

---

## Solana Top 5 漏洞 (对应你的50模式)

### 1. Missing Signer Check ≡ EVM Missing Access Control

```rust
// ❌ BUG: 不检查调用者身份
pub fn withdraw(ctx: Context<Withdraw>, amount: u64) -> Result<()> {
    **ctx.accounts.vault.try_borrow_mut_lamports()? -= amount;
    **ctx.accounts.user.try_borrow_mut_lamports()? += amount;
    // ⚠️ 任何人都能调用 — 没有 signer 检查!
}

// ✅ FIX: Anchor 自动检查 #[account(signer)]
pub fn withdraw(ctx: Context<Withdraw>, amount: u64) -> Result<()> {
    // Anchor 根据 #[account(signer)] 自动验证
}
```

### 2. PDA 种子碰撞 ≡ EVM CREATE2 Front-Running

```rust
// ❌ BUG: PDA 种子可被攻击者预测和使用
let (pda, bump) = Pubkey::find_program_address(
    &[b"vault", user.key().as_ref()],  // ⚠️ 没有唯一标识
    program_id
);

// ✅ FIX: 包含唯一标识
let (pda, bump) = Pubkey::find_program_address(
    &[b"vault", user.key().as_ref(), &user_nonce.to_le_bytes()],
    program_id
);
```

### 3. 跨程序调用(CPI)重入 ≡ EVM Reentrancy

```rust
// ❌ BUG: CPI 后状态被污染
pub fn deposit_and_stake(ctx: Context<DepositStake>, amount: u64) -> Result<()> {
    ctx.accounts.pool.deposit(amount)?;
    // ⚠️ 外部 CPI — 可能回调本程序!
    ctx.accounts.staking.stake(amount)?;
    ctx.accounts.user.deposited += amount;  // ⚠️ 之后才更新
}

// ✅ FIX: CEI 原则同样适用
pub fn deposit_and_stake(ctx: Context<DepositStake>, amount: u64) -> Result<()> {
    ctx.accounts.user.deposited += amount;  // 先更新状态
    ctx.accounts.pool.deposit(amount)?;     // 再外部调用
}
```

### 4. 账户数据反序列化缺失 ≡ EVM 不安全类型转换

```rust
// ❌ BUG: 不验证账户数据类型
pub fn process(ctx: Context<Process>, data: Vec<u8>) -> Result<()> {
    let mut account_data = ctx.accounts.target.try_borrow_mut_data()?;
    // ⚠️ 没有验证 account_data 的结构!
    account_data[0] = data[0];
}

// ✅ FIX: Anchor 自动反序列化+验证
// #[account(mut)] —— Anchor 自动检查 discriminator
```

### 5. 时钟操纵 ≡ EVM block.timestamp 攻击

```rust
// Solana 没有 block.timestamp — 用 Clock sysvar
// ❌ BUG: 用 Slot 作为时间源 (非确定性)
let clock = Clock::get()?;
if clock.slot % 100 == 0 {  // ⚠️ Slot ≠ 时间!
    distribute_rewards()?;
}
```

---

## 学习路径: 1小时能审第一个 Solana 合约

```bash
# 1. 安装工具链
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"
cargo install anchor-cli

# 2. 创建一个测试程序
anchor init my-solana-audit
cd my-solana-audit

# 3. 审计一个简单的漏洞程序 (我们自己写)
# programs/my-solana-audit/src/lib.rs

# 4. 运行测试
anchor test
```

---

## 你的优势

你有 50 个 EVM 模式 = 已经理解所有 DeFi 攻击原理。Solana 只是换了语言和账户模型，攻击本质不变：

| 你的 EVM 知识 | → Solana 等价 |
|------|------|
| 重入(CEI) | CPI 后状态污染 |
| 权限缺失 | Missing Signer Check |
| 存储碰撞 | PDA 种子碰撞 |
| 预言机操纵 | Clock/Slot 时间源 |
| 类型溢出 | 账户数据反序列化 |

---

## 实战: 用 Anchor 写第一个漏洞合约

```rust
use anchor_lang::prelude::*;

declare_id!("YourProgramID11111111111111111111111111");

#[program]
pub mod vault {
    use super::*;
    
    // ⚠️ BUG: 无 signer 检查 — 任何人可提款
    pub fn withdraw(ctx: Context<Withdraw>, amount: u64) -> Result<()> {
        let vault = &mut ctx.accounts.vault;
        let user = &mut ctx.accounts.user;
        
        // 直接转账 — 没有验证 user 是否签名!
        **vault.to_account_info().try_borrow_mut_lamports()? -= amount;
        **user.to_account_info().try_borrow_mut_lamports()? += amount;
        
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Withdraw<'info> {
    #[account(mut)]
    pub vault: AccountInfo<'info>,      // ⚠️ 缺少 #[account(signer)]
    #[account(mut)]
    pub user: AccountInfo<'info>,       // ⚠️ 也缺少
}
```

**这就是 Solana 上最常见的 $100M+ 漏洞类**。
