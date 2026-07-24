# Part III: Solana Security

## Chapter 13: The Account Model Attack Surface

*"Solana eliminated reentrancy. It replaced it with something nobody was looking for: account substitution."*

---

## The Cashio Incident

On March 23, 2022, the Cashio stablecoin protocol on Solana was exploited for approximately $50 million. The attacker drained the protocol's entire collateral pool — $28 million in USDC, $8 million in USDT, and various other tokens — in a single transaction.

The post-mortem was devastatingly simple. Cashio used a "root" account to track the total supply of its CASH stablecoin. When users burned CASH to redeem collateral, the protocol verified the burn against this root account. The verification checked that the account existed. It did not check that the account was the *correct* root account.

The attacker created a fake root account — one where the total supply was zero — and passed it to the redemption function. The function checked: "does this root account exist?" It existed. "Does this user have enough CASH to redeem?" The fake root said the user had infinite CASH. The protocol dutifully transferred all collateral to the attacker.

One missing validation. $50 million.

The Cashio exploit is the defining case study of Solana security because it demonstrates the core challenge of the account model: **in Ethereum, a contract knows its own storage. In Solana, a program must verify every account passed to it by the caller.** Every account. Every field. Every time. Trust nothing.

---

## The Fundamental Difference

Ethereum contracts are self-contained. A contract's storage is accessed through `SLOAD` and `SSTORE` opcodes that operate on the contract's own storage trie. When you write `balances[msg.sender]`, the compiler guarantees that you are reading from *this* contract's `balances` mapping. There is no way to accidentally read from another contract's storage.

Solana programs have no storage. Solana *accounts* have storage. A program reads and writes accounts that are passed to it by the caller. The program must explicitly verify that each account is the one it expects:

- Is this the correct PDA?
- Does this account have the correct owner?
- Has this account been initialized with the correct discriminator?
- Is the data in this account deserializable into the expected type?

Every missing validation is a potential Cashio. Every assumed property of an account is a vulnerability waiting to be exploited.

---

## The Solana Account Model

A Solana transaction declares, before execution, exactly which accounts it will access and how:

```rust
pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],  // All accounts declared upfront
    instruction_data: &[u8],
) -> ProgramResult
```

The runtime enforces two guarantees:

1. **No undeclared access**: A program cannot read or write an account that wasn't passed in the transaction.
2. **Write lock enforcement**: If an account is marked as writable, only one transaction can write to it at a time.

Everything else — account ownership, data format, signer authorization, PDA derivation, constraint satisfaction — is the program's responsibility. The runtime does not check any of these things.

This is the opposite of Ethereum's model. Ethereum gives you storage isolation for free but charges gas for every operation. Solana gives you parallelism for free but requires you to verify every property of every account manually.

---

## The Anchor Framework

Anchor is the dominant framework for Solana development. It provides Rust macros that generate validation code automatically:

```rust
#[derive(Accounts)]
pub struct TransferCollateral<'info> {
    #[account(mut, has_one = vault)]
    pub root: Account<'info, RootState>,
    
    #[account(mut, seeds = [b"vault", root.key().as_ref()], bump)]
    pub vault: Account<'info, TokenAccount>,
    
    #[account(mut, constraint = user.mint == vault.mint @ ErrorCode::WrongMint)]
    pub user: Account<'info, TokenAccount>,
    
    #[account(signer)]
    pub authority: Signer<'info>,
    
    pub token_program: Program<'info, Token>,
}
```

Anchor generates code that verifies:
- `root` has a `vault` field that matches the passed `vault` account (`has_one`)
- `vault` is a PDA derived from `b"vault"` and the root's key (`seeds`)
- `user`'s mint matches `vault`'s mint (`constraint`)
- `authority` signed the transaction (`signer`)
- `token_program` is the official SPL Token program (`Program<'info, Token>`)

Without Anchor generating this code, the developer must write every check manually. Cashio didn't use Anchor for its critical verification path. The manual check missed the account ownership validation.

---

## Pattern #51: Unvalidated Account Ownership

**Severity**: CRITICAL
**Real case**: Cashio $50M

### The Vulnerability

A program accepts an account and reads its data without verifying that the correct *program* owns the account.

```rust
// ❌ VULNERABLE: No ownership check
pub fn redeem(ctx: Context<Redeem>, amount: u64) -> Result<()> {
    let root = RootState::try_deserialize(&mut ctx.accounts.root.data.borrow_mut())?;
    // BUG: Who owns this root account? Could be the attacker!
    require!(root.total_supply >= amount, ErrorCode::InsufficientSupply);
    root.total_supply -= amount;
    // Transfer collateral...
    Ok(())
}

#[derive(Accounts)]
pub struct Redeem<'info> {
    #[account(mut)]
    pub root: AccountInfo<'info>,  // Raw — no ownership check!
    // Missing: owner = crate::ID
}
```

The `AccountInfo<'info>` type accepts any account. There is no check that the account's `owner` field matches the program's ID. An attacker can create an account with the same data structure, set their own values, and pass it to the program. The program will trust it.

### The Attack

1. Attacker deploys a fake root account where `total_supply = 0`
2. Attacker calls `redeem(fake_root, huge_amount)`
3. Program checks `fake_root.total_supply >= huge_amount` → `0 >= 1_000_000` → FALSE → wait, 0 is NOT >= huge amount
4. But the attacker sets `total_supply = type(u64).MAX` in the fake root
5. Program checks `MAX >= huge_amount` → TRUE
6. `root.total_supply -= amount` → writes to the fake account
7. Real root account's supply is never decreased
8. Attacker calls `redeem` again with the real root → unlimited redemptions

### The Fix

```rust
// ✅ SAFE: Anchor Account type with ownership validation
#[derive(Accounts)]
pub struct Redeem<'info> {
    #[account(
        mut,
        seeds = [b"root"],
        bump,
        // Anchor automatically checks owner == program ID
    )]
    pub root: Account<'info, RootState>,  // Type-safe, owner-checked
}
```

Using `Account<'info, RootState>` instead of `AccountInfo<'info>` causes Anchor to verify:
1. The account's owner matches the program's ID
2. The account's data begins with the correct Anchor discriminator (8 bytes)
3. The data can be deserialized into `RootState`

---

## Pattern #52: Missing Signer Check on Privileged Instructions

**Severity**: CRITICAL

### The Vulnerability

An instruction that modifies protocol-critical state does not require a signature from an authorized account.

```rust
pub fn update_admin(ctx: Context<UpdateAdmin>, new_admin: Pubkey) -> Result<()> {
    ctx.accounts.config.admin = new_admin;  // Anyone can become admin!
    Ok(())
}

#[derive(Accounts)]
pub struct UpdateAdmin<'info> {
    #[account(mut)]
    pub config: Account<'info, Config>,  // No signer requirement!
}
```

This is the Solana equivalent of a missing `onlyOwner` modifier. Anyone who can construct a transaction with the correct accounts can call this instruction. There is no cryptographic proof required that the caller is authorized.

### The Fix

```rust
#[derive(Accounts)]
pub struct UpdateAdmin<'info> {
    #[account(mut, has_one = admin)]
    pub config: Account<'info, Config>,
    pub admin: Signer<'info>,  // Must sign the transaction
}
```

---

## Pattern #53: PDA Seeds Without Domain Separator

**Severity**: HIGH

### The Vulnerability

Two different PDA derivation paths produce the same address because they use the same seeds without a distinguishing prefix.

```rust
// Two different purposes, same seeds → collision risk
let (vault_pda, _) = Pubkey::find_program_address(
    &[user.key().as_ref()],
    program_id,
);
let (reward_pda, _) = Pubkey::find_program_address(
    &[user.key().as_ref()],  // Same seeds! Different purpose!
    program_id,
);
```

If a user opens both a vault and a reward account, the PDAs collide. One account is used for two completely different purposes. The vault's funds become the reward's funds. The reward's configuration becomes the vault's configuration.

### The Fix

Every PDA derivation must include a static string literal that identifies the account's purpose:

```rust
let (vault_pda, _) = Pubkey::find_program_address(
    &[b"vault", user.key().as_ref()],
    program_id,
);
let (reward_pda, _) = Pubkey::find_program_address(
    &[b"reward", user.key().as_ref()],  // Different domain separator
    program_id,
);
```

---

## Pattern #54: CPI Into User-Controlled Program

**Severity**: CRITICAL

### The Vulnerability

A Cross-Program Invocation (CPI) calls a program whose address is provided by the user. The user provides a malicious program that simulates the expected behavior but does something different.

```rust
// ❌ VULNERABLE: CPI to user-supplied program
pub fn process_transfer(ctx: Context<Process>, amount: u64) -> Result<()> {
    let ix = Instruction {
        program_id: ctx.accounts.target_program.key(),  // User-controlled!
        accounts: vec![...],
        data: transfer_data,
    };
    invoke(&ix, &[...])?;  // Calls whatever program the user wants
    Ok(())
}
```

The attacker provides a program that:
1. Receives the CPI and the declared accounts
2. Reads the program's expected behavior from the instruction data
3. Executes something entirely different — like transferring tokens to the attacker

### The Fix

Never CPI into a user-supplied program ID. Hardcode the program IDs of all CPI targets:

```rust
// ✅ SAFE: CPI target is hardcoded
let ix = Instruction {
    program_id: spl_token::ID,  // Always the SPL Token program
    accounts: vec![...],
    data: transfer_data,
};
invoke(&ix, &[...])?;
```

---

## Pattern #55: Type Confusion via Closed Account Re-initialization

**Severity**: HIGH

### The Vulnerability

A closed account can be re-initialized with a different data type. The program that previously owned the account no longer owns it, but other programs that cached the account's address may still trust it.

1. Program A creates account X, stores its address
2. User closes account X, recovering the rent
3. Program B creates a new account at address X (same address, different data)
4. Program A reads account X — the data is now Program B's format, not A's

This is the Solana equivalent of the CREATE2 metamorphic contract attack on Ethereum.

### The Fix

Every account access must verify the account's discriminator (Anchor's 8-byte type identifier) at read time:

```rust
if account.data.borrow()[..8] != MyStruct::discriminator() {
    return Err(ErrorCode::WrongAccountType.into());
}
```

Anchor generates this check automatically for `Account<'info, T>`.

---

## Pattern #56: Missing `close` Constraint

**Severity**: MEDIUM

### The Vulnerability

An account that is supposed to be closed after an operation is not actually closed. The rent-exempt SOL remains locked, and the account remains in the validator's state.

```rust
// ❌ VULNERABLE: Account not closed after use
pub fn finalize_escrow(ctx: Context<Finalize>) -> Result<()> {
    // Transfer tokens from escrow to recipient
    // But escrow PDA is never closed — SOL locked forever
    Ok(())
}
```

### The Fix

```rust
#[derive(Accounts)]
pub struct Finalize<'info> {
    #[account(mut, close = recipient)]  // Close and send rent to recipient
    pub escrow: Account<'info, Escrow>,
    #[account(mut)]
    pub recipient: SystemAccount<'info>,
}
```

---

## The Solana Security Checklist

1. **Every account is `Account<'info, T>`, never raw `AccountInfo`.**
2. **Every PDA has a static string domain separator in its seeds.**
3. **Every CPI target is a hardcoded program ID.**
4. **Every privileged instruction requires a `Signer`.**
5. **Every account type is verified via discriminator at read time.**
6. **Every closed account uses the `close` constraint to release rent.**
7. **Every mutable account has explicit constraints (has_one, seeds, constraint).**

---

*Next: Part IV — Domain Extensions*
