# DeFi Security Dataset — Continuous Maintenance Plan for 2027

*Version: 2026-07-17*

---

## 1. Current State

| Metric | Value |
|--------|-------|
| Incidents tracked | 824 (2017-07 through 2026-06) |
| Data sources | DeFiHackLabs (PoC contracts), Rekt News, SlowMist, CertiK |
| Last major update | 2026-07 (Paper 06 taxonomy validation) |
| Next target | 2027 version with 1000+ incidents |

---

## 2. Monthly Maintenance Routine

### Week 1: Ingest
- Scrape Rekt News leaderboard for new entries
- Check DeFiHackLabs GitHub for new PoC contracts
- Monitor SlowMist Hacked archive
- Check CertiK, PeckShield, BlockSec Twitter/Medium for incident reports
- Add any new incidents to the master dataset

### Week 2: Classify
- Apply 50-pattern taxonomy to new incidents
- Flag incidents that don't fit existing patterns → candidate for new pattern
- Update category statistics
- Check for temporal pattern shifts

### Week 3: Validate
- Cross-reference incident reports across sources
- Verify loss figures from multiple sources
- Update TVL data from DeFiLlama
- Recalculate Risk Index

### Week 4: Publish
- Update dataset on GitHub
- Generate monthly statistics report
- Tweet/publish key findings
- Plan paper updates if significant new patterns emerge

---

## 3. Key Metrics to Track

| Metric | Update Frequency | Source |
|--------|-----------------|--------|
| Total incidents | Monthly | Dataset |
| Total losses (USD) | Monthly | Dataset |
| DeFi Risk Index (loss/TVL) | Monthly | Dataset + DeFiLlama |
| Top attack vectors by count | Monthly | Dataset |
| Top attack vectors by loss | Monthly | Dataset |
| Median loss | Monthly | Dataset |
| New pattern emergence | Monthly | Manual review |
| Protocol TVL tier distribution | Quarterly | DeFiLlama |
| Audit coverage rate | Quarterly | Manual/Crunchbase |
| Bug bounty program count | Quarterly | Immunefi |

---

## 4. Infrastructure Improvements

### Short-term (Q3 2026):
- [ ] Automated incident scraper for Rekt News
- [ ] GitHub Actions CI for monthly dataset validation
- [ ] Automated classification using LLM + pattern matching
- [ ] Dashboard for real-time metrics

### Medium-term (Q4 2026 - Q1 2027):
- [ ] Contract-level linking (map incidents to verified contracts on Etherscan)
- [ ] Cross-chain incident tracking (Solana, Cosmos, Move)
- [ ] Lost fund recovery tracking (tornado cash, MEV bots, white-hat recovery)
- [ ] Attacker profiling (known groups, repeat attackers)

### Long-term (2027+):
- [ ] Real-time incident alert system (Telegram/Discord bot)
- [ ] Predictive risk scoring for new protocols
- [ ] Integration with audit firm databases
- [ ] Regulatory incident classification (for compliance)

---

## 5. Paper Update Schedule

| Paper | Update Trigger | Next Version |
|-------|---------------|--------------|
| **04** Decade Analysis | 1000+ incidents or new era identified | v2.0 (2027-Q1) |
| **06** Taxonomy | New pattern discovered (currently 50) | v1.2 (when pattern #51+ emerges) |
| **07** Hardening Gradient | Significant gradient shift | v2.0 (annual recalibration) |
| **08** EIP-712 Errors | Additional 100+ contract analysis | v1.2 (2027) |

---

## 6. Contribution Guidelines

### Adding a new incident:
1. Verify from at least 2 independent sources
2. Capture: date, protocol, chain, loss USD, attack vector, root cause, PoC link
3. Classify using 50-pattern taxonomy
4. Submit PR to dataset repository

### Proposing a new attack pattern:
1. Must have at least 3 independent incidents
2. Must not fit comfortably within existing patterns
3. Describe mechanism, canonical example, detection approach
4. Submit proposal for review before taxonomy update

---

## 7. Zenodo Versioning

- Each major dataset update → new Zenodo version
- Papers referencing the dataset should cite the latest Zenodo DOI
- Maintain backwards compatibility (old DOIs still resolve)
- Include changelog in each Zenodo deposition

---

*End of maintenance plan.*
