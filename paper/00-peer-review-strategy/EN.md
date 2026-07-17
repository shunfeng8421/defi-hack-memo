# Peer Review Submission Strategy — Papers 04, 06, 07

*Prepared: 2026-07-17 | Author: Shiqiang Chen (IIE, CAS)*

---

## 1. Paper Ranking & Venue Recommendations

| Paper | Grade | Best Venue | Backup Venue | Submission Window |
|-------|-------|------------|--------------|-------------------|
| **07** Hardening Gradient | **A+** | **WEIS 2027** (Feb deadline) | ACM CCS 2027 (May) | Q1-Q2 2027 |
| **06** Taxonomy | **A** | **ACM Computing Surveys** (rolling) | IEEE S&P 2027 (Dec) | Rolling / Q4 2026 |
| **04** Decade Analysis | **A−** | **Financial Cryptography 2027** (Sep) | ACM AFT 2027 | Q3 2026 |

### Rationale:

**Paper 07 (Hardening Gradient)** — The strongest theoretical contribution. Fits WEIS (Workshop on Economics of Information Security) perfectly due to the security economics modeling. The hardening gradient concept, security elasticity model, and vulnerability floor are exactly the type of contributions WEIS values. ACM CCS is a strong backup.

**Paper 06 (Taxonomy)** — ACM Computing Surveys is ideal for survey/taxonomy papers. It accepts rolling submissions and values comprehensive reference works. This paper will become the canonical DeFi attack taxonomy; placing it in CSUR maximizes its reference value. IEEE S&P is a backup for prestige.

**Paper 04 (Decade Analysis)** — Financial Cryptography values empirical DeFi security studies. The decade-scale analysis fits FC's interest in longitudinal security studies. ACM AFT (Advances in Financial Technologies) is a natural backup.

---

## 2. Pre-Submission Checklist

### For all three papers:

- [ ] Convert from Markdown to LaTeX (ACM/IEEE template)
- [ ] Anonymize author information for double-blind venues
- [ ] Expand related work section with latest citations
- [ ] Add formal statistical tests where appropriate
- [ ] Deposit preprint on arXiv before submission
- [ ] Prepare supplementary materials (datasets, code)

### Paper-specific:

**Paper 07**:
- [ ] Strengthen causal claims (instrumental variables? diff-in-diff?)
- [ ] Add non-EVM chain analysis (Solana, Cosmos)
- [ ] Derive security elasticity parameters from granular data
- [ ] Recruit economics co-author for WEIS submission

**Paper 06**:
- [ ] Move pattern descriptions to appendix (paper too long at 1140 lines)
- [ ] Benchmark Slither rule FP/FN rates
- [ ] Reduce self-citation count
- [ ] Add inter-rater reliability for category assignment

**Paper 04**:
- [ ] Recruit statistics co-author for methodological rigor
- [ ] Add quasi-experimental analysis
- [ ] Expand limitations section
- [ ] Consider merging with Paper 03 (see consolidation analysis)

---

## 3. Cover Letter Templates

### 3.1 Paper 07 — Hardening Gradient (WEIS 2027)

```
Dear WEIS Program Committee,

We submit "The Hardening Gradient: How DeFi Security Inequality Is Reshaping
the Attack Surface" for consideration at WEIS 2027.

This paper introduces a novel theoretical framework — the hardening gradient —
to explain a paradox in DeFi security: aggregate metrics show both
deterioration (rising hack losses) and improvement (declining risk/TVL).
Through analysis of 824 confirmed DeFi incidents (2017-2026), we demonstrate
that this apparent contradiction is resolved by a structural bifurcation:
large protocols ($1B+ TVL) reduced incidents by 75%, while small protocols
(under $1M TVL) experienced a 178% increase.

Our key contributions are:
1. The hardening gradient concept — a formal model of security bifurcation
   by protocol TVL, validated with statistical significance (χ²=47.3,
   p<0.0001)
2. A security elasticity model relating TVL to optimal security investment,
   with derivation of the $5M TVL "vulnerability floor"
3. A policy framework for closing the gradient: pooled audit subsidies,
   progressive pricing, automated infrastructure, risk-based insurance
4. Formal derivation of the gap between individual and collective security
   optima, providing theoretical justification for intervention

We believe this paper aligns strongly with WEIS's focus on the economics of
information security. The hardening gradient has implications for audit firm
pricing, insurance underwriting, protocol design, and regulatory frameworks.

The associated dataset (824 incidents) and analysis code are released under
MIT license.

Sincerely,
Shiqiang Chen
Institute of Information Engineering, Chinese Academy of Sciences
```

### 3.2 Paper 06 — Taxonomy (ACM Computing Surveys)

```
Dear Editor,

We submit "A Comprehensive Taxonomy of DeFi Attack Patterns: 50 Vectors from
824 Incidents" for consideration in ACM Computing Surveys.

This paper presents the largest and most comprehensive taxonomy of DeFi
attack patterns to date. Existing taxonomies capture 8-12 patterns with at
best 58% coverage. Our taxonomy identifies 50 distinct attack vectors across
7 categories, achieving 97.6% coverage against 824 confirmed incidents
spanning 2017-2026.

Key contributions:
1. A 50-pattern DeFi attack taxonomy, each with mechanism description,
   canonical incident examples, detection methodology, and Slither rule
   mapping
2. Statistical characterization: 8 patterns account for 76% of all losses;
   flash loan + oracle manipulation represents 24% of cases and 60% of
   losses (>$6B)
3. Detection gap analysis: 12 patterns (24%) lack Slither rules; 18 patterns
   (36%) require business-logic understanding beyond static analysis
4. An open-source 50-rule DeFi scanner for community use

As a comprehensive reference work, we believe this taxonomy is well-suited
for CSUR's mission of publishing surveys that become standard references in
their field. Every subsequent DeFi security paper, audit report, and
educational material will benefit from a standardized, empirically validated
attack classification.

The complete taxonomy, all 50 detection rules, and the scanner are released
under MIT license.

Sincerely,
Shiqiang Chen
```

### 3.3 Paper 04 — Decade Analysis (Financial Cryptography 2027)

```
Dear FC Program Committee,

We submit "A Decade of DeFi Attacks: Pattern Evolution, Risk Dynamics, and
the Fragmentation of the Attack Surface" for consideration at Financial
Cryptography 2027.

This paper presents the first decade-scale empirical analysis of DeFi
security incidents, synthesizing data from 824 confirmed exploits spanning
2017-2026. Our key findings challenge conventional narratives about DeFi
security:

1. The dominant attack vector shifted from high-value flash loans (median
   $15M, 2020-21) to small-scale permission bugs (median $50K, 2025) — a
   300× reduction in median loss
2. The DeFi Risk Index (loss/TVL) declined 30% (3.33% → 2.33%), demonstrating
   measurable security maturation
3. A "hardening gradient" emerged: large protocols ($1B+ TVL) hardened, while
   small protocols (<$1M TVL) continued falling to basic bugs
4. The 2026 attack landscape introduces a novel class combining precision
   errors, intentional backdoors, and accounting inconsistencies

We believe FC's audience of financial cryptography researchers and
practitioners will find this longitudinal analysis valuable for understanding
the security trajectory of decentralized finance.

The dataset and analysis scripts are released under MIT license.

Sincerely,
Shiqiang Chen
```

---

## 4. Timeline

```
2026-Q3 (Jul-Sep):
  - Paper 04: Format for FC 2027 (Sep deadline)
  - All: Deposit preprints on arXiv
  - Begin co-author recruitment for Papers 04, 07

2026-Q4 (Oct-Dec):
  - Paper 06: Submit to ACM Computing Surveys
  - Paper 04: Submit to FC 2027
  - Integrate reviewer feedback

2027-Q1 (Jan-Mar):
  - Paper 07: Submit to WEIS 2027 (Feb deadline)
  - Monitor Paper 04, 06 review status

2027-Q2 (Apr-Jun):
  - Paper 07: Submit to CCS 2027 (May, if WEIS rejected)
  - Respond to reviewer revisions
```

---

## 5. Co-Author Recruitment Strategy

### Paper 07 (Hardening Gradient) — Economics Expert Needed

**Ideal profile**: Researcher with expertise in security economics, financial economics, or mechanism design. Experience with empirical economic analysis, causal inference methods (IV, DiD, RDD), and security economics literature.

**Potential targets**:
- WEIS regular contributors
- Economics of security researchers at CMU, Harvard, UC Berkeley
- Crypto-economics researchers at Ethereum Foundation, a16z crypto research
- Financial econometricians with crypto interest

**Pitch**: "I have a paper that introduces a novel concept — the hardening gradient — with strong empirical grounding (824 incidents) and a formal security elasticity model. It needs an economics co-author to strengthen the causal inference, refine the economic model, and position it for WEIS."

### Paper 04 (Decade Analysis) — Statistician Needed

**Ideal profile**: Statistician or data scientist with experience in longitudinal analysis, time series, or survival analysis. Familiarity with Bayesian methods or quasi-experimental design would strengthen causal claims.

**Potential targets**:
- Statistics department colleagues at CAS
- Data science researchers with DeFi interest
- Quantitative security researchers

**Pitch**: "This is the largest empirical dataset of DeFi security incidents ever compiled (824 incidents over 10 years). I need a statistics co-author to apply rigorous longitudinal analysis methods, strengthen the statistical testing, and identify temporal patterns that simple descriptive statistics miss."

---

## 6. Papers 03-04 Consolidation Analysis

### Current State:
- **Paper 03**: "DeFi Attack Evolution: The Flash Loan Revolution" (482 lines)
  - Focus: Flash loan attacks across three eras (2020-2021, 2021-2023, 2024-2026)
  - 8-pattern flash loan taxonomy
  - Hardening Paradox, defense code evolution
  
- **Paper 04**: "A Decade of DeFi Attacks" (978 lines)
  - Focus: All attack vectors, full 2017-2026 period
  - 17-pattern taxonomy
  - Risk Index, hardening gradient, 2026 landscape

### Overlap Analysis:
- Both cover temporal evolution
- Both introduce the hardening gradient concept
- Paper 04's 17-pattern taxonomy subsumes Paper 03's 8-pattern flash loan subset
- Paper 03 provides deeper analysis of flash loans specifically

### Consolidation Options:

**Option A: Merge into "Decade Analysis"** (Recommended)
- Make Paper 03 Section 4 of Paper 04 ("Flash Loan Evolution Case Study")
- Consolidate taxonomies: Paper 04 uses Paper 06's 50-pattern reference, Paper 03's 8 patterns become detailed subsections
- Result: One strong paper with comprehensive coverage
- Risk: Paper 04 already long at 978 lines; adding Paper 03 material would make it ~1460 lines

**Option B: Keep separate, differentiate clearly**
- Paper 03 becomes a focused "Flash Loan Defense Evolution" paper
- Remove hardening gradient from Paper 03 (it's Paper 07's contribution)
- Position Paper 03 as the practitioner-oriented deep-dive on flash loans
- Paper 04 remains the comprehensive decade analysis

**Option C: Three-way consolidation**
- Merge Papers 03 + 04 into Paper 06 chapter structure
- Paper 06 becomes a monograph rather than a paper
- This would consolidate all "what happened" content into one reference work
- Risk: Paper 06 already 1140 lines

### Recommendation: **Option B** — Keep separate but differentiate clearly. Paper 03 is valuable as a focused deep-dive on flash loans with practical code examples. Paper 04 is the comprehensive decade analysis. Remove overlapping hardening gradient content from Paper 03 (let Paper 07 carry that concept). Add explicit cross-references between all four papers.

---

*End of peer review strategy document.*
