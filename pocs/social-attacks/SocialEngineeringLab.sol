// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Social Engineering Attack Lab — The Human Layer
/// @notice Ronin $625M was not a code bug. It was a human being convinced.
/// @author Shiqiang Chen · July 2026

// ============================================================
// The Invisible Attack Surface
// ============================================================
// Every protocol you audit has a security model:
//   "Funds are safe if 5-of-9 validators sign"
//   "Upgrades require multi-sig approval"
//   "Emergency pause requires 3 admin signatures"
//
// These are not technical guarantees. They are social ones.
// The code enforces that 5 signatures are required.
// The code does not enforce that 5 humans will refuse to be tricked.

// ============================================================
// Attack #1: Discord/Social Impersonation
// ============================================================
contract Attack1_Impersonation {
    // The most common entry point for $1M+ exploits.
    // Not a smart contract vulnerability.
    //
    // Attack chain:
    // 1. Attacker creates Discord account "Admin_Support"
    // 2. DMs a project developer: "Urgent security upgrade needed"
    // 3. Sends a malicious contract address as "the fix"
    // 4. Developer — under pressure, tired, trusting — approves
    // 5. Funds drained
    //
    // Real: Multiple DeFi projects in 2022-2024
    // Defense: NEVER execute based on Discord DM. Ever.
    //   All actions go through on-chain governance + timelock.
    //   No exception. No "emergency" that bypasses this.
}

// ============================================================
// Attack #2: The Fake Job Interview
// ============================================================
contract Attack2_FakeInterview {
    // Attack chain:
    // 1. Attacker posts fake job listing for "Blockchain Dev"
    // 2. Victim applies, goes through realistic interview process
    // 3. "Final round: here's a coding test" → malicious repo
    // 4. Victim runs `npm install` or `forge test` → malware
    // 5. Attacker now has victim's private keys, SSH access, etc.
    //
    // Real: Axie Infinity Ronin Bridge — the attacker socially
    // engineered a senior engineer through a fake job offer,
    // gaining access to Sky Mavis infrastructure
    //
    // Defense: Development machines never hold production keys.
    //   Hardware wallets for all signing operations.
    //   Code review for any dependency added to build pipeline.
}

// ============================================================
// Attack #3: The Urgent Upgrade
// ============================================================
contract Attack3_UrgentUpgrade {
    // Attack chain:
    // 1. Attacker identifies a real but non-critical bug
    // 2. Sends "URGENT: Critical vulnerability found"
    // 3. Provides "patch" that actually introduces backdoor
    // 4. Team — panicked, rushing — deploys without full review
    //
    // The urgency is the weapon. Humans under time pressure
    // skip verification steps they would normally perform.
    //
    // Real: The Nomad $152M bug was introduced during an
    // upgrade. The team was rushing to add features.
    //
    // Defense: No upgrade without 48h timelock — period.
    //   If the bug is truly critical, 48h is still faster
    //   than the time it takes to recover from a bad upgrade.
}

// ============================================================
// Attack #4: The Insider Threat
// ============================================================
contract Attack4_Insider {
    // The hardest attack to defend against.
    // The attacker already has access. They are on the team.
    //
    // Real: Multiple exchange hacks involved insiders
    // Real: The original DAO hacker may have been a developer
    //
    // Defense: Principle of least privilege.
    //   No single person can:
    //   - Deploy contracts (requires 2-of-3)
    //   - Access production keys (requires hardware + physical)
    //   - Approve upgrades (requires multi-sig with timelock)
    //   - Access all infrastructure (separated by role)
    //
    // Every permission is explicitly granted, time-limited,
    // and revocable without notice.
}

// ============================================================
// Attack #5: The Phishing Contract
// ============================================================
contract Attack5_PhishingContract {
    // Attacker deploys a contract that looks legitimate:
    // - Same name as popular protocol (Uniswap → Un1swap)
    // - Same interface (identical function signatures)
    // - Same parameters (appears to do the right thing)
    //
    // Victim approves token spend → attacker drains wallet
    //
    // Defense: Contract address verification.
    //   Never trust the name. Always verify the address
    //   against the official source (docs, Twitter, GitHub).
    //   Consider using ENS for human-readable verification.
}

// ============================================================
// Attack #6: Bribe the Guardians
// ============================================================
contract Attack6_Bribery {
    // A multi-sig requires 4-of-7 guardians.
    // The attacker offers each guardian $1M to sign.
    // If 4 accept, the protocol loses $100M.
    //
    // This is not a code vulnerability. It is an economic one.
    // Security threshold < bribery budget = protocol is vulnerable.
    //
    // Defense: Guardian selection.
    //   Guardians must have:
    //   - Reputation at stake (public figures, known entities)
    //   - Economic alignment (hold protocol tokens long-term)
    //   - Jurisdictional diversity (can't all be prosecuted together)
    //   - Organizational diversity (can't all be fired together)
}

// ============================================================
// The Social Engineering Defense Checklist
// ============================================================
// 1. NO ACTION happens via Discord DM, Telegram, or email.
//    Everything goes through on-chain governance with timelock.
//
// 2. NO UPGRADE happens without 48h minimum timelock.
//    "Emergency" is not an exception. It's how Ronin happened.
//
// 3. NO SINGLE PERSON has deploy or upgrade authority.
//    Multi-sig with organizational diversity.
//
// 4. PRODUCTION KEYS never touch development machines.
//    Hardware wallets. Air-gapped signing. Multi-party ceremonies.
//
// 5. VERIFY, THEN TRUST. Contract addresses from official sources.
//    News from official channels. Urgency is a red flag, not a green light.
//
// 6. ASSUME YOU ARE THE TARGET. Social engineers don't target
//    protocols they think are unworthy. If you're being targeted,
//    your protocol has value. Act accordingly.

// ============================================================
// Summary
// ============================================================
// The biggest exploits in DeFi history were not code bugs:
//   Ronin $625M    — Social engineering (fake job offer)
//   PolyNetwork $610M — Missed access control (human error)
//   Nomad $152M    — One-character typo during upgrade
//   Wormhole $326M — Missed patch from Solana upgrade
//
// The pattern: HUMANS are the attack surface.
// Code audits audit code. They do not audit humans.
// If your security model assumes humans will make good
// decisions under pressure, your security model is wrong.
