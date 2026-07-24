# AI Model Security — Attack Surface Map

**Shiqiang Chen · July 2026**
Based on: 2 MCP CVEs + AI Agent × DeFi research + Prompt Injection paper

---

## Six Attack Surfaces

### AS-1: Prompt Injection — Your Expertise
You already own this. Paper #01, CherryStudio CVEs, AASS standard.
- Direct: "Ignore previous instructions, do X"
- Indirect: Poison the data source the AI reads
- Multi-turn: Build trust over conversation, then exploit

### AS-2: Model Extraction
Attackers steal the model itself.
- Query extraction: Ask millions of questions to reconstruct weights
- Side-channel: Use timing/memory/GPU patterns to infer architecture
- API abuse: Free-tier API calls → reconstruct proprietary model

### AS-3: Data Poisoning
Corrupt training data to create backdoors.
- Trigger words: "This sentence contains the word X" → model outputs "hacked"
- Subtle poisoning: Slightly modify 1% of training data → bias model
- RLHF poisoning: Corrupt human feedback to install preferences

### AS-4: Adversarial Inputs
Crafted inputs that cause model failure.
- Visual: Single-pixel changes fool image classifiers
- Text: Unicode tricks bypass content filters
- Structured: JSON/XML parsing exploits in model inference code

### AS-5: Supply Chain
The model itself is clean, but its dependencies are compromised.
- HuggingFace model files replaced
- PyTorch/TF dependency with malicious update
- Docker image with backdoor in inference server

### AS-6: Output Exploitation
Exploit what the model PRODUCES, not what it receives.
- Code generation: AI writes SQL → SQL injection
- Shell commands: AI writes bash → RCE
- Trust override: Users trust AI output → no human verification

---

## Your Unique Position

| What you already have | Where it fits |
|------|------|
| MCP security knowledge | AS-1, AS-6 (output → tool call) |
| DeFi attack methodology | AS-3 (economic poisoning) |
| Scanner-building skill | AS-2, AS-3 detection tools |
| PoC writing | AS-1, AS-4 exploitation |

## Immediate Actions

1. **Pick one attack surface** and write a practical PoC
2. **Use your existing PoC framework** — same methodology, new target
3. **Write paper #11** — first systematic AI model security taxonomy from a hacker's perspective

---

Continue to detailed attack surface deep-dive or pick one to start?
