#!/usr/bin/env python3
"""
ZK Circuit Security Scanner — Detect vulnerabilities in Circom/Noir/Halo2 code.
Author: Shiqiang Chen · July 2026
"""
import os, re, json, sys
from collections import defaultdict

PATTERNS = {
    "UNCONSTRAINED_SIGNAL": {
        "severity": "CRITICAL",
        "regex": [
            r'(\w+)\s*<--\s*',  # Assignment without constraint
            r'signal\s+\w+\s*;.*\n(?!.*<==)',  # Signal declared but never constrained
        ],
        "keyword": ["<--", "signal"],
        "description": "Signal assigned with <-- instead of <== — prover can forge value. DO NOT USE <-- for any variable that affects proof correctness.",
        "fix": "Use <== for all signals that affect the proof output. Only use <-- for intermediate computation."
    },
    "MISSING_RANGE_CHECK": {
        "severity": "HIGH",
        "regex": [
            r'signal\s+input\s+\w+\s*;',  # Input signal without range check
        ],
        "keyword": ["signal input", "!<", "!LessThan", "!Num2Bits"],
        "description": "Input signal has no range check — attacker can submit arbitrarily large values that wrap around modulo p.",
        "fix": "Add component { check = Num2Bits(252); check.in <== input; } to constrain input size."
    },
    "OVERFLOW_WRAPPING": {
        "severity": "HIGH",
        "regex": [
            r'(\w+)\s*<==\s*(\w+)\s*\+\s*(\w+)',  # Addition without overflow check
            r'(\w+)\s*<==\s*(\w+)\s*\*\s*(\w+)',  # Multiplication without overflow check
        ],
        "keyword": ["+", "*", "!Num2Bits", "!LessThan"],
        "description": "Arithmetic without overflow protection — values can wrap around the prime field p.",
        "fix": "Add overflow guards: signal result <== a + b; result <== a * b; then check result < 2^252."
    },
    "PUBLIC_INPUT_LEAK": {
        "severity": "HIGH",
        "regex": [
            r'signal\s+output\s+hash',  # Hash exposed as output
            r'signal\s+output\s+commitment',
        ],
        "keyword": ["signal output", "hash", "poseidon", "mimc", "!nullifier", "!salt"],
        "description": "Public output may leak private information via hash matching. Ensure output doesn't expose secret-derived values.",
        "fix": "Use salted commitments: output <== Poseidon([secret, salt]); never expose secret directly."
    },
    "UNBOUNDED_LOOP": {
        "severity": "MEDIUM",
        "regex": [
            r'for\s*\(\s*var\s+\w+\s*=\s*\d+\s*;\s*\w+\s*<.*?;\s*\w+\+\+\)',
        ],
        "keyword": ["for", "var"],
        "description": "Loop with VAR-bound condition — must be compile-time constant. VAR-loop limits unknown at proof generation.",
        "fix": "Use for (var i = 0; i < CONSTANT_VALUE; i++) where CONSTANT_VALUE is a known literal."
    },
    "COMPONENT_UNINITIALIZED": {
        "severity": "MEDIUM",
        "regex": [
            r'component\s+(\w+)\s*;.*?\n(?!.*\1\s*=|.*\1\.)',
        ],
        "keyword": ["component", "!=", "!."],
        "description": "Component declared but never used or initialized — circuit logic missing.",
        "fix": "Ensure every declared component is used with .in <== values and produces .out."
    },
}

class ZKScanner:
    def __init__(self, target_dir: str):
        self.target = target_dir
        self.findings = []
        self.stats = {"files": 0, "lines": 0}
    
    def scan_file(self, filepath: str, source: str):
        for pid, pattern in PATTERNS.items():
            found_lines = []
            for regex in pattern["regex"]:
                for i, line in enumerate(source.split('\n'), 1):
                    if re.search(regex, line):
                        found_lines.append(i)
            
            kw_match = True
            for kw in pattern["keyword"]:
                if kw.startswith('!'):
                    if kw[1:] in source:
                        kw_match = False
                        break
                elif kw not in source:
                    kw_match = False
                    break
            
            if found_lines or kw_match:
                self.findings.append({
                    "file": os.path.basename(filepath),
                    "id": pid,
                    "severity": pattern["severity"],
                    "description": pattern["description"],
                    "fix": pattern["fix"],
                    "lines": found_lines[:3]
                })
    
    def scan_directory(self):
        for root, _, files in os.walk(self.target):
            for f in files:
                if f.endswith('.circom'):
                    fp = os.path.join(root, f)
                    try:
                        with open(fp, encoding='utf-8', errors='replace') as fh:
                            source = fh.read()
                        self.stats["files"] += 1
                        self.stats["lines"] += source.count('\n')
                        self.scan_file(fp, source)
                    except:
                        pass
        return self
    
    def report(self) -> str:
        sev = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0}
        for f in self.findings:
            sev[f["severity"]] += 1
        
        lines = [
            "# ZK Circuit Security Audit",
            f"\n**Target**: {self.target}",
            f"**Files**: {self.stats['files']} | **Lines**: {self.stats['lines']}",
            f"**Findings**: {len(self.findings)} (🔴{sev['CRITICAL']} 🟠{sev['HIGH']} 🟡{sev['MEDIUM']})\n",
            "## Findings\n"
        ]
        for f in self.findings:
            emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}[f["severity"]]
            lines.append(
                f"### {emoji} {f['id']} — {f['file']}\n"
                f"- **Issue**: {f['description']}\n"
                f"- **Fix**: {f['fix']}\n"
                f"- **Lines**: {', '.join(map(str, f['lines'])) if f['lines'] else 'N/A'}\n"
            )
        return '\n'.join(lines)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    scanner = ZKScanner(target)
    scanner.scan_directory()
    print(scanner.report())
