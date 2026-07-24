#!/usr/bin/env python3
"""
Bridge Security Scanner — CBSS v1.0 compliant
Automated cross-chain bridge vulnerability detection across 6 attack surfaces.
Author: Shiqiang Chen · July 2026
"""
import os, re, json, sys
from collections import defaultdict

# 6 Bridge Attack Surface Patterns
BRIDGE_PATTERNS = {
    "AS-1": {
        "name": "Message Verification Bypass",
        "severity": "CRITICAL",
        "regex": [
            r'(?:abi\.decode|decodePayload|_processPayload)\s*\(',
            r'messageId\s*==\s*0x0|messageHash\s*==\s*bytes32\(0\)',
        ],
        "keyword": ["decode", "verify", "!validateMessage", "!recover"],
        "description": "Incoming cross-chain message may not be properly verified",
        "fix": "Validate message format, signer, and nonce before processing"
    },
    "AS-2": {
        "name": "Validator Collusion Risk",
        "severity": "CRITICAL",
        "regex": [
            r'(?:required|threshold)\s*[<>=]+\s*\d+',
            r'validators\.length\s*/\s*2',
        ],
        "keyword": ["validator", "threshold", "quorum", "signer"],
        "description": "Validator threshold may allow collusion attack",
        "fix": "Require ≥2/3 validator signatures on every message"
    },
    "AS-3": {
        "name": "Cross-Chain Replay",
        "severity": "CRITICAL",
        "regex": [
            r'keccak256\s*\(.*(?!.*chainId|.*block\.chainid)',
            r'ecrecover\s*\(.*(?!.*chainId)',
        ],
        "keyword": ["keccak256", "signature", "!chainId", "!block.chainid"],
        "description": "Signed message lacks chainId — replayable on other chains",
        "fix": "Include chainId + nonce + deadline in every signed message"
    },
    "AS-4": {
        "name": "Mint/Burn Asymmetry",
        "severity": "CRITICAL",
        "regex": [
            r'function\s+mint\s*\(.*(?!.*only\w+)',
            r'function\s+burn\s*\(.*(?!.*only\w+)',
        ],
        "keyword": ["mint", "burn", "!mintAndBurn", "!verifyBurn", "!checkSupply"],
        "description": "Mint without corresponding burn validation — supply attack",
        "fix": "Always verify burn event on source chain before minting"
    },
    "AS-5": {
        "name": "Upgradeability Attack",
        "severity": "HIGH",
        "regex": [
            r'(?:upgradeTo|upgradeToAndCall)\s*\(',
            r'_authorizeUpgrade\s*\(',
        ],
        "keyword": ["upgrade", "!timelock", "!multisig", "!delay"],
        "description": "Bridge implementation can be upgraded without timelock",
        "fix": "Require timelock + multi-sig for any implementation upgrade"
    },
    "AS-6": {
        "name": "Stuck Fund Recovery",
        "severity": "HIGH",
        "regex": [
            r'function\s+(?:emergency|rescue|recover)\s*\w*\s*\(',
        ],
        "keyword": ["emergencyWithdraw", "rescue", "parked", "!recover", "!rescue"],
        "description": "Failed cross-chain delivery has no recovery path",
        "fix": "Implement emergency withdrawal for parked/stuck funds"
    },
}

class BridgeScanner:
    def __init__(self, target_dir: str):
        self.target = target_dir
        self.findings = []
        self.stats = {"files": 0, "lines": 0}
    
    def scan_file(self, filepath: str, source: str):
        for aid, pattern in BRIDGE_PATTERNS.items():
            found_lines = []
            for regex in pattern["regex"]:
                for i, line in enumerate(source.split('\n'), 1):
                    if re.search(regex, line, re.IGNORECASE):
                        found_lines.append(i)
            
            # Keyword check: must find all positive keywords and NO negative keywords
            kw_match = True
            for kw in pattern["keyword"]:
                if kw.startswith('!'):
                    if kw[1:] in source.lower():
                        kw_match = False
                        break
                elif kw.lower() not in source.lower():
                    kw_match = False
                    break
            
            if found_lines or kw_match:
                self.findings.append({
                    "file": os.path.basename(filepath),
                    "id": aid,
                    "name": pattern["name"],
                    "severity": pattern["severity"],
                    "description": pattern["description"],
                    "fix": pattern["fix"],
                    "lines": found_lines[:3]
                })
    
    def scan_directory(self):
        for root, _, files in os.walk(self.target):
            for f in files:
                if f.endswith('.sol'):
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
        severity = {"CRITICAL": 0, "HIGH": 0}
        for f in self.findings:
            severity[f["severity"]] += 1
        
        lines = [
            f"# Bridge Security Audit — CBSS v1.0",
            f"\n**Target**: {self.target}",
            f"**Files**: {self.stats['files']} | **Lines**: {self.stats['lines']}",
            f"**Findings**: {len(self.findings)} (🔴{severity['CRITICAL']} 🟠{severity['HIGH']})\n",
            "## Critical & High Findings\n"
        ]
        
        for f in self.findings:
            if f["severity"] in ("CRITICAL", "HIGH"):
                lines.append(
                    f"### {'🔴' if f['severity']=='CRITICAL' else '🟠'} {f['id']}: {f['name']} — {f['file']}\n"
                    f"- **Issue**: {f['description']}\n"
                    f"- **Fix**: {f['fix']}\n"
                    f"- **Lines**: {', '.join(map(str, f['lines'])) if f['lines'] else 'N/A'}\n"
                )
        
        return '\n'.join(lines)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "/tmp/cherum/src"
    scanner = BridgeScanner(target)
    scanner.scan_directory()
    print(scanner.report())
    json.dump(scanner.findings, open(os.path.join(target, "bridge-scan.json"), "w"), indent=2)
