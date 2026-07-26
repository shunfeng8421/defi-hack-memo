# On-Chain Forensics: 3 Rapid Reconstructions

## 1. OlympusDAO — Fake Token Redemption ($292K, 30,437 OHM)

```
┌──────────────────────────────────────────┐
│ OlympusDAO BondFixedExpiryTeller          │
│                                            │
│ redeem(token, amount)                      │
│   → accepts ANY token with correct decimals│
│   → redeems at OHM price                   │
│                                            │
│ Attack:                                     │
│ 1. Deploy fake token (matching decimals)   │
│ 2. Mint large amount of fake token         │
│ 3. redeem(fakeToken, hugeAmount)           │
│    → BondTeller thinks it's OHM            │
│    → Sends real OHM for fake token         │
│ 4. Profit: 30,437 OHM (~$292K)             │
└──────────────────────────────────────────┘
```
**Pattern**: Token Validation Failure — Contract trusts any token with matching interface.  
**Fix**: Whitelist specific accepted tokens. `require(token == OHM)`.

---

## 2. Spartan Protocol — Liquidity Pool Manipulation ($30.5M)

```
┌──────────────────────────────────────────┐
│ SpartanSwap Liquidity Pools                │
│                                            │
│ addLiquidity → get shares                  │
│ removeLiquidity → burn shares for assets   │
│                                            │
│ Attack:                                     │
│ 1. Flash loan large amount of token A      │
│ 2. Swap A for B on SpartanSwap             │
│    → Manipulates pool ratio                │
│ 3. addLiquidity(manipulated ratio)         │
│    → Gets inflated shares                  │
│ 4. removeLiquidity(all shares)             │
│    → Gets more assets than deposited       │
│ 5. Repay flash loan + profit              │
└──────────────────────────────────────────┘
```
**Pattern**: Flash Loan + Pool Ratio Manipulation — Liquidity shares calculated at manipulated prices.  
**Fix**: Minimum lockup period for liquidity positions.

---

## 3. Pawnfi — Oracle Exploit ($820K)

```
┌──────────────────────────────────────────┐
│ Pawnfi Lending Protocol                    │
│                                            │
│ Collateral value = oracle.getPrice(token)  │
│ Oracle: spot price from DEX                │
│                                            │
│ Attack:                                     │
│ 1. Flash loan → manipulate DEX price       │
│ 2. Deposit inflated collateral             │
│ 3. Borrow against inflated value           │
│ 4. Repay flash loan                        │
│ 5. Profit: borrowed funds > flash loan fee │
└──────────────────────────────────────────┘
```
**Pattern**: Pattern #1 — Flash Loan + Spot Price Oracle.
**Fix**: TWAP oracle with minimum 30-minute window.
