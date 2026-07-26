# Chapter 24: Incident Response Checklist

*"You will be attacked. The question is: what happens in the first 60 seconds?"*

---

## The First 60 Seconds

An exploit transaction confirms on Etherscan. The monitoring alert fires. The protocol's Telegram and Discord light up with panicked messages. Every second that passes, more funds are at risk. What do you do?

This is not a hypothetical. This has happened to over 100 DeFi protocols since 2020. The difference between those that recovered and those that didn't was not code quality—it was response time and decision-making under pressure. Here is the checklist that every protocol should have printed, laminated, and accessible to every team member.

### Phase 1: Containment (First 60 Seconds)

| # | Action | Rationale |
|:--:|------|------|
| 1 | **Trigger the circuit breaker.** If you have a pause function, call it NOW. Every second costs money. | Nomad lost $152M in under 2 hours. Beanstalk lost $182M in 13 seconds. A 60-second pause saves everything. |
| 2 | **Identify the attack vector.** What contract was called? What function? What parameters? | The transaction on Etherscan tells you everything the attacker did. Read the input data. Trace the internal calls. |
| 3 | **Assess the blast radius.** Is the attack ongoing or completed? Are other contracts affected? | If the attack was a single transaction, the immediate danger may have passed. If the vulnerability is still exploitable, every block brings another loss. |
| 4 | **Lock admin keys.** If administrative functions (upgrade, pause, withdraw) are not protected by timelock, the attacker may try to use them next. | Ronin's attacker gained control of 5-of-9 validators. If the attacker can upgrade your contracts, they can drain everything. |

### Phase 2: Assessment (First 5 Minutes)

| # | Action | Rationale |
|:--:|------|------|
| 5 | **Run the 58-pattern scanner on the affected contracts.** | The scanner identifies known vulnerability patterns in seconds. If the exploit matches a known pattern, you already know the fix. |
| 6 | **Preserve on-chain evidence.** Download all transaction traces, event logs, and state diffs. | The attacker's address, transaction hash, and call sequence are evidence. Preserve them before block explorers reorganize or cache clears. |
| 7 | **Identify the attacker's exit path.** Where did the stolen funds go? Tornado Cash? CEX deposit address? Bridge? | If the funds moved to a centralized exchange, you have minutes—not hours—to contact the exchange and request a freeze. |

### Phase 3: Communication (First 15 Minutes)

| # | Action | Rationale |
|:--:|------|------|
| 8 | **Post a brief, factual statement.** "We are investigating a potential security incident. Funds are [safe/at risk]. Updates to follow." | Silence is interpreted as complicity. A brief statement buys time for investigation without spreading panic. |
| 9 | **Do NOT speculate about cause, loss amount, or attacker identity.** | Every incorrect statement will be screenshotted, quoted, and used against you later. State only verifiable facts. |
| 10 | **Contact security partners.** Reach out to your auditor, bug bounty platform, and incident response firms. | Multiple independent analyses reduce the chance of missing the root cause. |

### Phase 4: Remediation (First 60 Minutes)

| # | Action | Rationale |
|:--:|------|------|
| 11 | **Deploy the fix.** If the vulnerability is in a contract you control, patch and redeploy. If it's in an external dependency, contact the dependency maintainer. | A fix that introduces a new vulnerability is worse than no fix. Testing under time pressure is dangerous. |
| 12 | **Restore paused functionality.** Once the fix is deployed and verified, unpause with caution. Start with a small amount of TVL. | Gradual restoration reduces risk if the fix is incomplete. |
| 13 | **Monitor the attacker's address.** Even after the incident, watching where the stolen funds move can provide intelligence. | Stolen funds that move to a CEX can still be frozen. Stolen funds that sit idle may indicate the attacker is waiting for attention to die down. |

---

## User Communication: What to Say and When

The most common mistake in incident response is not technical. It is communication. Protocols either say nothing—creating a vacuum filled by speculation—or say too much—making incorrect statements that damage credibility.

### The First Statement (Within 15 Minutes)

> "We are aware of unusual activity affecting [Protocol Name]. Our team is investigating. We will provide a detailed update shortly. In the meantime, all contracts have been paused as a precaution. User funds that were not actively involved in the affected pool are safe."

Key elements:
- Acknowledge the incident without confirming an exploit
- State actions taken (pause)
- Provide a timeline for next update
- Reassure users about unaffected funds

### The Post-Mortem (Within 48 Hours)

A post-mortem is a technical document that explains what happened, why, and what will prevent it from happening again. The Truebit post-mortem discussed in Chapter 3 is exemplary. A good post-mortem includes:

1. **Timeline**: Exact timestamps of every material event
2. **Root cause**: The specific code or process failure that enabled the attack
3. **Impact**: Funds lost, users affected, recovery status
4. **Fix**: The technical change that prevents recurrence
5. **Lessons**: What the protocol learned and how it will change

### What NOT to Do

- **Blame the attacker**: The attacker exploited a vulnerability you left in your code. Focus on fixing your code, not vilifying the attacker.
- **Promise full reimbursement before assessing losses**: If the loss exceeds your treasury, you cannot make good on the promise.
- **Delete the post-mortem later**: The community remembers. Protocols that delete their post-mortems are seen as covering up mistakes.

---

## The Bug Bounty Disclosure Template

The author has submitted five responsible disclosure reports. Each follows a consistent format:

```
Subject: Security Vulnerability Report — [Product] [Brief Description]

Body:
1. IDENTITY: Name, GitHub profile, affiliation
2. VULNERABILITY: What it is, how it works, severity (CRITICAL/HIGH/MEDIUM)
3. PROOF OF CONCEPT: Enough detail to reproduce, not enough to exploit
4. FIX RECOMMENDATION: Specific, actionable, with code
5. DISCLOSURE TIMELINE: When the report was sent, when public disclosure is planned

The format is professional because the recipient is professional. A security report is not a bug report. It is a business communication.
```

**Critical Rule**: Verify the protocol's bug bounty program rules before reporting. Some programs explicitly forbid certain types of testing. Sending an unsolicited exploit demonstration to a protocol without a bug bounty program can be interpreted as an attack attempt.

---

## The Security Researcher's Responsibility

If you are reading this book, you are probably not a victim of the attacks described here. You are someone who wants to prevent them. That comes with a responsibility.

**When you find a vulnerability**:
1. Give the protocol time to fix it before publishing
2. Don't exploit it for profit
3. Don't sell it to someone who will
4. Verify the protocol has a bug bounty program or security contact before reporting
5. If the protocol does not respond, follow responsible disclosure timelines (90 days standard)

**The hardening gradient** (Chapter 1) means that large protocols have resources to respond to disclosures. Small protocols may not. Your disclosure could save a protocol that would otherwise be exploited. Or it could destroy a protocol that cannot handle the public revelation of a vulnerability. Choose your approach accordingly.

---

## Epilogue

We began this book with a counterintuitive observation: DeFi is getting safer for large protocols and more dangerous for small ones—the hardening gradient. We end with a challenge: **close the gap.**

Every pattern in this book—all 58 detection rules, all 105 Foundry tests, all 24 chapters—is infrastructure that any protocol can use, regardless of audit budget. Security expertise should not be measured by how much a protocol can pay for a Trail of Bits audit. It should be measured by knowledge, and knowledge should be free.

If this book helps one protocol avoid becoming the next Beanstalk, the next Nomad, the next Uranium—if one developer reads Chapter 6 and adds an access control check before deploying, if one auditor reads Chapter 5 and catches an oracle manipulation before it reaches mainnet, if one researcher reads Chapter 22 and builds their own scanner—it has served its purpose.

The hardening gradient is real. But it is not inevitable. When every protocol has access to the same security knowledge, the gradient flattens. That is the goal of this book. That is the goal of every tool, every test, and every pattern documented here.

Close the gap.

---

*End of Handbook*
