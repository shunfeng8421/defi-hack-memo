# Tare Protocol — Audit Pre-Mortem (Pre-Scope Analysis)

## Protocol Overview
- **Type**: On-chain loan exchange for institutional credit
- **Standard**: ERC-7540 (Asynchronous Tokenized Vault)
- **Features**: Asset-level NFTs, double-entry accounting, programmatic settlement
- **Contest**: $50K USDC, July 20-29, Sherlock

## ERC-7540 Attack Surface

ERC-7540 extends ERC-4626 with async deposit/redeem:
- `requestDeposit()` → pending shares
- `requestRedeem()` → pending assets
- `claimDeposit()` / `claimRedeem()` → finalize
- Introduces **time gap** between request and claim

### Potential Vulnerabilities

| # | Vector | Risk |
|:--:|------|:--:|
| 1 | **Deposit request → share price change** → claim gets different value than expected | HIGH |
| 2 | **Redeem request → asset value change** → withdraw more/less than fair | HIGH |
| 3 | **Claim front-running** → attacker claims before victim, takes their shares | MEDIUM |
| 4 | **ERC-4626 inflation** → first depositor attack applies to ERC-7540 too | MEDIUM |
| 5 | **Request ID manipulation** → claim with wrong request ID | MEDIUM |
| 6 | **Unclaimed requests accumulation** → DoS via pending queue | LOW |

## Loan-Specific Attack Vectors

| # | Vector | Pattern Ref |
|:--:|------|:--:|
| 7 | **Interest rate manipulation** → oracle for loan pricing | #1 Flash Loan Oracle |
| 8 | **Collateral ratio gaming** → deposit → borrow → withdraw before price update | #6 Liquidation |
| 9 | **Double-spend of loan proceeds** → async settlement gap | #17 Sig Replay |
| 10 | **NFT ownership vs loan claim conflict** → who owns collateral? | #8 Governance |
| 11 | **Accounting drift** → double-entry ≠ single-entry sum | #47 Accounting |
| 12 | **Settlement timing attack** → manipulate price at settlement moment | #1 Oracle |

## Pre-Scan Checklist

When repo drops:
- [ ] Clone + count contracts
- [ ] Run `defi-scanner` on all code
- [ ] Manual review: ERC-7540 claim/deposit/redeem flows
- [ ] Check oracle price sources (TWAP? Chainlink? Spot?)
- [ ] Audit NFT ownership transfer logic
- [ ] Verify double-entry accounting = on-chain state
- [ ] Test async settlement timing edge cases
- [ ] Cross-check access control on all admin functions

## Expected Finding Classes
1. **Oracle manipulation** — if loan pricing uses spot AMM prices
2. **ERC-7540 race conditions** — request vs claim timing
3. **Accounting bugs** — settlement math errors
4. **Access control** — admin functions on loan lifecycle
