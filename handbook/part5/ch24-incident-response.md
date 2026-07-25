# Chapter 24: Incident Response

*"You will be attacked. The question is: what happens in the first 60 seconds?"*

---

## The First 60 Seconds

An exploit transaction is confirmed on Etherscan. The monitoring alert fires. The protocol's Telegram and Discord light up with panicked messages. Every second that passes, more funds are at risk. What do you do?

1. **Pause the protocol.** If you have a circuit breaker, trigger it immediately. Every second of delay costs money.
2. **Identify the attack vector.** What contract was called? What function? What parameters? The transaction on Etherscan tells you everything.
3. **Assess the blast radius.** Is the attack ongoing? Has it stopped? Is the attacker likely to strike again? If the attack was a single transaction, the immediate danger may have passed. If the vulnerability is still exploitable, every subsequent transaction is another loss.
4. **Communicate.** Users need to know: what happened, are their funds safe, what should they do. Silence is interpreted as complicity.

---

## The Four Bug Bounty Emails

The author has submitted four responsible disclosure reports:

| Target | Vulnerability | Response |
|------|------|------|
| Gitea | Auth bypass (CVE-2026-20896) | Pending |
| Vercel/NextJS | SSRF (CVE-2025-29927) | Pending |
| n8n | Sandbox escape (CVE-2026-1470) | Pending |
| Sangoma/FreePBX | SQL injection | Pending |

Each report follows a consistent format:

1. **Concise subject**: "Security Vulnerability Report — [Product] [CVE]"
2. **Identity**: Name, GitHub profile, affiliation (independent researcher)
3. **Vulnerability description**: What it is, how it works, severity
4. **Proof of concept**: Enough detail to reproduce, not enough to exploit
5. **Fix recommendation**: Specific, actionable, with code if applicable
6. **Disclosure timeline**: When the report was sent, when public disclosure is planned

The format is professional because the recipient is professional. A security report is not a bug report. It is a business communication. It should be written accordingly.

---

## After the Incident

Once the immediate threat is contained:

1. **Post-mortem**: A detailed technical report explaining what happened, why, and how it was fixed. The Truebit post-mortem discussed in Chapter 3 is a model for this.
2. **User compensation**: If funds were lost, how will users be made whole? Ronin reimbursed users from Sky Mavis's reserves. Beanstalk could not.
3. **Process improvement**: What allowed this vulnerability to exist? Was it missed in audit? Introduced in an upgrade? What will prevent the next one?
4. **Public disclosure**: Publish the post-mortem. The community learns from every incident. Protocols that hide their failures condemn others to repeat them.

---

## The Security Researcher's Responsibility

If you are reading this book, you are probably not a victim of the attacks described here. You are someone who wants to prevent them. That comes with a responsibility.

When you find a vulnerability, disclose it responsibly. Give the protocol time to fix it before publishing. Don't exploit it for profit. Don't sell it to someone who will.

The hardening gradient means that large protocols have the resources to respond to disclosures. Small protocols may not. Your disclosure could save a protocol that would otherwise be exploited. Or it could destroy a protocol that cannot handle the public revelation of a vulnerability. Choose your approach accordingly.

This book has given you the tools to find vulnerabilities. Use them to protect, not to exploit. The DeFi ecosystem is fragile enough already.

---

## Epilogue

We began this book with a counterintuitive observation: DeFi is getting safer for large protocols and more dangerous for small ones—the hardening gradient. We end with a challenge: close the gap.

Every pattern in this book—all 58 detection rules, all 105 Foundry tests, all 24 chapters—is infrastructure that any protocol can use. Security expertise should not be measured by audit budget. It should be measured by knowledge, and knowledge should be free.

If this book helps one protocol avoid becoming the next Beanstalk, the next Nomad, the next Uranium, it has served its purpose.

---

*End of Handbook*
