# Part III: Solana Security

## Chapter 13: The Solana Attack Surface

*"Solana doesn't have reentrancy. It has something worse: account confusion."*

---

## Why Solana Is Different

The Ethereum security model is built around a single execution context: one contract, one storage space, one call stack. Reentrancy is possible because a contract can call another contract, which can call back. Every vulnerability in Part II — flash loans, oracle manipulation, access control failures — exploits this shared execution model.

Solana has no shared execution model. Every instruction in a Solana transaction specifies exactly which accounts it will read from and write to. The runtime validates these permissions before execution. You cannot read an account you haven't declared. You cannot write an account you haven't marked as writable. You cannot call an instruction without passing the accounts it needs.

This sounds more secure. In some ways, it is. Solana has no reentrancy — the runtime's account isolation prevents it. Solana has no delegatecall — there is no EVM-style code delegation. Solana has no selfdestruct — accounts cannot delete themselves.

But Solana replaces these familiar attack vectors with a new class of vulnerabilities that are specific to its architecture. These vulnerabilities are less well-understood, less documented, and less defended against than their Ethereum counterparts. This chapter covers the most dangerous ones.

---

## Pattern #51: Missing Signer Check

**Severity**: CRITICAL

### The Vulnerability

A Solana instruction modifies critical state but does not verify that the transaction was signed by an authorized account. Anyone who can construct a transaction that includes the required accounts can call the instruction.

```rust
// ❌ VULNERABLE: No signer check on admin account
pub fn update_fee(ctx: Context<UpdateFee>, new_fee: u64) -> Result<()> {
    ctx.accounts.config.fee = new_fee;  // Anyone can change this!
    Ok(())
}

#[derive(Accounts)]
pub struct UpdateFee<'info> {
    #[account(mut)]
    pub config: Account<'info, Config>,  // No #[account(signer)]!
}
```

The `config` account is marked as mutable (`mut`), allowing anyone to write to it. But there is no `#[account(signer)]` attribute requiring the config account to have signed the transaction. Anyone can submit a transaction with the correct account addresses and change the fee.

### The Fix

```rust
// ✅ SAFE: Signer required
#[derive(Accounts)]
pub struct UpdateFee<'info> {
    #[account(mut, signer)]  // Must sign the transaction
    pub admin: Signer<'info>,
    #[account(mut)]
    pub config: Account<'info, Config>,
}
```

The `Signer` type and `#[account(signer)]` attribute ensure that only the private key holder can authorize the instruction.

---

## Pattern #52: PDA Seed Collision

**Severity**: HIGH

### The Vulnerability

Program Derived Addresses (PDAs) are Solana accounts controlled by a program rather than a private key. A PDA is derived from a set of seeds and a program ID. If two different accounts can be derived from the same seeds — or if an attacker can predict the seeds that will be used — the attacker can create a conflicting account.

```rust
// ❌ VULNERABLE: Seeds lack unique identifiers
let (pda, bump) = Pubkey::find_program_address(
    &[user.key().as_ref(), amount.to_le_bytes().as_ref()],
    program_id,
);
// If the same user deposits the same amount twice, PDA collision!
```

### The Fix

Every PDA seed set must include at least one unique identifier — typically a counter, a nonce, or a unique string literal:

```rust
// ✅ SAFE: Includes campaign ID as unique identifier
let (pda, bump) = Pubkey::find_program_address(
    &[
        b"escrow",                     // Static domain separator
        campaign.key().as_ref(),       // Unique per campaign
        user.key().as_ref(),           // Unique per user
        &campaign.escrow_nonce.to_le_bytes(),  // Anti-collision nonce
    ],
    program_id,
);
```

The static string literal (`b"escrow"`) ensures that PDAs for different purposes within the same program cannot collide. The nonce ensures that repeated operations create unique accounts.

---

## Pattern #53: CPI Without Signer Seeds

**Severity**: HIGH

### The Vulnerability

Cross-Program Invocation (CPI) allows one Solana program to call another. When a program needs to act as the authority for a PDA, it must provide the PDA's signer seeds during the CPI. Without them, the PDA cannot sign the CPI, and the call fails — or worse, succeeds with the wrong authority.

```rust
// ❌ VULNERABLE: CPI without signer seeds
let transfer_ix = transfer(
    &token_program.key(),
    &pda_token_account.key(),  // PDA is the owner
    &destination.key(),
    &pda.key(),                // PDA must sign
    &[],
    amount,
)?;
invoke(&transfer_ix, &[pda_token_account.to_account_info()]);
// PDA is not signing! Transfer will fail.
```

### The Fix

```rust
// ✅ SAFE: Signer seeds provided
let seeds = &[
    b"vault",
    user.key().as_ref(),
    &[bump],
];
let signer_seeds = &[&seeds[..]];
invoke_signed(
    &transfer_ix,
    &[pda_token_account.to_account_info(), pda.to_account_info()],
    signer_seeds,  // PDA signs through its seeds
)?;
```

---

## Pattern #54: Unchecked Account Data

**Severity**: HIGH

### The Vulnerability

Anchor provides `Account<'info, T>` which automatically deserializes and validates account data. But raw `AccountInfo<'info>` bypasses this validation:

```rust
// ❌ VULNERABLE: Raw AccountInfo — no type validation
pub fn process(ctx: Context<Process>, data: Vec<u8>) -> Result<()> {
    let account_data = &mut ctx.accounts.target.data.borrow_mut();
    // Attacker can pass ANY account — wrong type, wrong owner, wrong data
}
```

### The Fix

```rust
// ✅ SAFE: Anchor Account type with validation
#[derive(Accounts)]
pub struct Process<'info> {
    #[account(mut)]
    pub target: Account<'info, TargetAccount>,  // Type-checked
    // Anchor validates: owner == program ID, data matches struct, discriminator correct
}
```

---

## Pattern #55: Clock/Slot Manipulation

**Severity**: MEDIUM

### The Vulnerability

Solana's `Clock` sysvar provides the current slot number and timestamp. Using `Clock::get()?.slot` as a source of randomness or uniqueness is dangerous — the slot is predictable, and within a single slot, it is the same for all transactions.

```rust
let clock = Clock::get()?;
let random_id = clock.slot;  // Not random! Same for all txns in this slot.
```

### The Fix

Use a commit-reveal scheme or a verifiable random function for randomness. Never use `slot` or `unix_timestamp` as a source of unpredictability.

---

## Pattern #56: Missing `has_one` Constraint

**Severity**: HIGH

### The Vulnerability

Anchor's `#[account]` macro provides `has_one` constraints that verify an account field matches another account in the instruction. Without it, an attacker can provide an account that the program assumes is linked but isn't.

```rust
// ❌ VULNERABLE: No has_one constraint
#[derive(Accounts)]
pub struct Withdraw<'info> {
    pub vault: Account<'info, Vault>,
    pub authority: Signer<'info>,
    // Attacker can pass any vault!
}
```

### The Fix

```rust
// ✅ SAFE: has_one validates authority
#[derive(Accounts)]
pub struct Withdraw<'info> {
    #[account(has_one = authority)]  // vault.authority == authority.key()
    pub vault: Account<'info, Vault>,
    pub authority: Signer<'info>,
}
```

---

## Pattern #57: Arithmetic Overflow

**Severity**: MEDIUM

### The Vulnerability

Unlike Solidity 0.8+, Solana's Rust programs do not have automatic overflow protection. Arithmetic on `u64` values silently wraps:

```rust
let reward = amount * multiplier;  // May overflow without warning
```

### The Fix

```rust
let reward = amount.checked_mul(multiplier)
    .ok_or(ErrorCode::Overflow)?;  // Explicit overflow check
```

---

## Pattern #58: Token CPI Without Validation

**Severity**: HIGH

### The Vulnerability

A program performs a token transfer CPI without first verifying the token program ID, the mint, or the account ownership:

```rust
// ❌ VULNERABLE: No token program validation
let transfer_ix = transfer(
    ctx.accounts.token_program.key,  // Attacker can pass fake token program
    &from,
    &to,
    &authority,
    &[],
    amount,
)?;
invoke(&transfer_ix, &[...])?;
```

### The Fix

```rust
// ✅ SAFE: Validate token program
require!(
    ctx.accounts.token_program.key() == spl_token::ID,
    ErrorCode::InvalidTokenProgram
);
require!(
    ctx.accounts.mint.key() == expected_mint,
    ErrorCode::InvalidMint
);
```

---

## Solana Security Checklist

1. **Every mutable account has `signer` or `has_one` constraint.** No exceptions.
2. **Every PDA has a unique domain separator in its seeds.** `b"escrow"`, `b"vault"`, etc.
3. **Every CPI with a PDA includes signer seeds.** Never invoke without them.
4. **Every account is an `Account<'info, T>` — never raw `AccountInfo`.** Raw mode is only for advanced cases with explicit validation.
5. **Every arithmetic operation uses `checked_*`.** No silent wrapping.
6. **Every token program is validated against `spl_token::ID`.** Never trust a user-supplied token program.

---

*Next: Part IV — Domain Extensions (MEV, Governance, Lending, DEX, DePIN, ZK, RWA, GameFi, AI)*
