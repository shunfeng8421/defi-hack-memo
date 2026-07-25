# SESA — Social Engineering Security Assessment v1.0

## Run

```bash
python sesa.py          # Interactive assessment
python sesa.py --demo   # Show all vulnerabilities
```

## The 6 Attack Vectors

| # | Vector | Real Case | Loss |
|:--:|------|------|--:|
| 1 | Discord Impersonation | Multiple DeFi hacks | Varies |
| 2 | Fake Job Interview | Ronin Bridge | $625M |
| 3 | Urgent Upgrade Pressure | Nomad Bridge | $152M |
| 4 | Insider Threat | Exchange hacks | Varies |
| 5 | Phishing Contracts | Fake Uniswap/AAVE | Varies |
| 6 | Guardian Bribery | Governance exploits | Varies |

## Output

- Overall risk score (0-100%)
- Per-vector breakdown with severity bars
- Top 3 actionable improvements
- Real case comparison

## The One Rule

**No code vulnerability matters if a human can be tricked into giving away the keys.**
