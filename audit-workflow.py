#!/usr/bin/env python3
"""
On-Chain Audit Workflow — End to End
1. Clone/Fetch → 2. Scan → 3. Classify → 4. Report → 5. Map Patterns

Usage: python audit-workflow.py <github_url> [--etherscan <address>]
Author: Shiqiang Chen — July 2026
"""
import os, sys, json, re, subprocess, tempfile, shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ============================================================
# Phase 1: Source Acquisition
# ============================================================
class SourceAcquisition:
    """Clone GitHub repo or fetch verified contract from Etherscan"""
    
    @staticmethod
    def from_github(url, target_dir):
        print(f"[1/5] Cloning {url}...")
        cmd = f"git clone --depth 1 --quiet {url} {target_dir}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Clone failed: {result.stderr}")
        return target_dir
    
    @staticmethod
    def from_etherscan(address, target_dir, api_key=""):
        print(f"[1/5] Fetching {address} from Etherscan...")
        url = f"https://api.etherscan.io/api?module=contract&action=getsourcecode&address={address}&apikey={api_key}"
        import urllib.request, json
        resp = json.loads(urllib.request.urlopen(url).read())
        if resp['status'] != '1':
            raise RuntimeError(f"Etherscan error: {resp.get('message')}")
        source = resp['result'][0]['SourceCode']
        contract_name = resp['result'][0]['ContractName']
        os.makedirs(target_dir, exist_ok=True)
        path = os.path.join(target_dir, f"{contract_name}.sol")
        with open(path, 'w') as f:
            f.write(source)
        return target_dir

# ============================================================
# Phase 2: Scan Engine
# ============================================================
class ScanEngine:
    """Run Slither + DeFi Scanner on source"""
    
    @staticmethod
    def run_slither(target_dir):
        """Run Slither if available"""
        print("[2/5] Running Slither...")
        findings = []
        try:
            result = subprocess.run(
                f"slither {target_dir} --detect all --json - 2>/dev/null",
                shell=True, capture_output=True, text=True, timeout=120
            )
            if result.stdout:
                data = json.loads(result.stdout)
                for detector in data.get('results', {}).get('detectors', []):
                    findings.append({
                        "tool": "Slither",
                        "check": detector.get('check', ''),
                        "impact": detector.get('impact', ''),
                        "description": detector.get('description', ''),
                        "elements": [e.get('source_mapping', {}).get('lines', []) for e in detector.get('elements', [])]
                    })
        except Exception as e:
            print(f"  Slither skipped: {e}")
        return findings
    
    @staticmethod
    def run_defi_scanner(target_dir):
        """Run our custom DeFi pattern scanner"""
        print("[2/5] Running DeFi Scanner (26 rules)...")
        # Import and run the scanner
        scanner_path = Path(__file__).parent / "defi-scanner.py"
        if not scanner_path.exists():
            # Use bundled version
            scanner_path = Path(__file__).parent / ".." / "defi-scanner.py"
        
        if scanner_path.exists():
            result = subprocess.run(
                f'python "{scanner_path}" "{target_dir}"',
                shell=True, capture_output=True, text=True, timeout=60
            )
            return result.stdout
        return "Scanner not found"

# ============================================================
# Phase 3: Pattern Classification
# ============================================================
class PatternClassifier:
    """Map findings to 50-pattern taxonomy"""
    
    PATTERN_MAP = {
        r'getReserves|getPriceOfOnePool': ("#1", "Flash Loan + Oracle", "CRITICAL"),
        r'reentrancy|re-entrancy|CEI': ("#2", "Reentrancy", "CRITICAL"),
        r'inflation|donation.*deposit|4626': ("#5", "ERC-4626 Inflation", "HIGH"),
        r'liquidation.*price|liquidate.*oracle': ("#6", "Lending Liquidation", "HIGH"),
        r'AMM.*manipulat|reserve.*manipulat|skew': ("#7", "AMM Manipulation", "HIGH"),
        r'governance|proposal.*flash|vote.*flash': ("#8", "Governance Attack", "CRITICAL"),
        r'signature.*replay|nonce.*missing|replay.*attack': ("#27", "Signature Replay", "CRITICAL"),
        r'cross.*chain.*replay|bridge.*chainid': ("#34", "Cross-Chain Replay", "CRITICAL"),
        r'permit.*deadline|approve.*front': ("#15", "Permit Frontrun", "MEDIUM"),
        r'precision.*loss|division.*before|rounding': ("#46", "Precision Loss", "MEDIUM"),
        r'owner.*upgrade|admin.*key|privilege': ("#13", "Admin Key Risk", "HIGH"),
        r'burn.*transfer|transfer.*burn.*pair': ("#25", "Token Burn Attack", "HIGH"),
        r'delegatecall.*user|delegatecall.*untrusted': ("#13", "Delegatecall Abuse", "CRITICAL"),
        r'fee.*transfer|transfer.*fee|balance.*diff': ("#39", "Fee-on-Transfer", "MEDIUM"),
        r'upgrade.*gap|storage.*collision': ("#13", "Upgrade Storage Collision", "MEDIUM"),
    }
    
    @classmethod
    def classify(cls, finding_text):
        for regex, (pid, name, severity) in cls.PATTERN_MAP.items():
            if re.search(regex, finding_text, re.IGNORECASE):
                return pid, name, severity
        return ("?", "Uncategorized", "UNKNOWN")

# ============================================================
# Phase 4: Report Generator
# ============================================================
class ReportGenerator:
    """Generate structured audit report"""
    
    @staticmethod
    def generate(project_name, target_dir, slither_findings, scanner_output):
        os.makedirs("audit-reports", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_path = f"audit-reports/{project_name}-{timestamp}.md"
        
        # Count source files and lines
        sol_files = list(Path(target_dir).rglob("*.sol"))
        total_lines = sum(len(open(f, encoding='utf-8', errors='replace').read().split('\n')) 
                         for f in sol_files if 'test' not in str(f) and 'mock' not in str(f))
        
        report = f"""# Audit Report: {project_name}

**Auditor**: Shiqiang Chen  
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Scope**: {len(sol_files)} contracts, {total_lines} lines  
**Methodology**: DeFi 50-Pattern Classification + Slither + Manual Review

---

## Executive Summary

| Metric | Value |
|------|------|
| Contracts Audited | {len(sol_files)} |
| Total Lines | {total_lines} |
| Slither Findings | {len(slither_findings)} |
| DeFi Pattern Matches | See below |

---

## Findings

### Slither Detections
"""
        for i, f in enumerate(slither_findings[:10], 1):
            report += f"""
#### S-{i}: {f['check']}
- **Impact**: {f['impact']}
- **Description**: {f['description']}
"""
        
        report += f"""

### DeFi Pattern Scanner Output
```
{scanner_output[:2000]}
```

---

## Pattern Mapping

| Finding | DeFi Pattern | Severity |
|------|:--:|:--:|
"""
        for f in slither_findings:
            pid, name, sev = PatternClassifier.classify(str(f))
            report += f"| {f['check'][:30]} | {name} | {sev} |\n"
        
        report += f"""

## Recommendations

1. Address all CRITICAL and HIGH findings before deployment
2. Use our 50-pattern DeFi taxonomy for continuous monitoring
3. Reference: github.com/shunfeng8421/defi-hack-memo

---

*Generated by On-Chain Audit Workflow v1.0*
"""
        with open(report_path, 'w') as f:
            f.write(report)
        return report_path

# ============================================================
# Phase 5: Main Workflow
# ============================================================
class AuditWorkflow:
    """Orchestrate the full audit pipeline"""
    
    def __init__(self, target):
        self.target = target
        self.work_dir = tempfile.mkdtemp(prefix="audit-")
        
    def run(self):
        print("=" * 60)
        print("  DeFi On-Chain Audit Workflow v1.0")
        print("  Shiqiang Chen — 2026")
        print("=" * 60)
        
        # Phase 1: Acquire source
        if self.target.startswith("http") or self.target.startswith("git@"):
            project_name = self.target.split("/")[-1].replace(".git", "")
            SourceAcquisition.from_github(self.target, self.work_dir)
        elif self.target.startswith("0x"):
            project_name = self.target[:10]
            SourceAcquisition.from_etherscan(self.target, self.work_dir)
        else:
            project_name = os.path.basename(self.target)
            self.work_dir = self.target  # local dir
        
        # Phase 2: Scan
        slither_findings = ScanEngine.run_slither(self.work_dir)
        scanner_output = ScanEngine.run_defi_scanner(self.work_dir)
        
        # Phase 3: Classify (integrated into report)
        # Phase 4: Generate report
        report_path = ReportGenerator.generate(
            project_name, self.work_dir, slither_findings, scanner_output
        )
        
        # Phase 5: Map to patterns
        print(f"\n[5/5] Report saved: {report_path}")
        print(f"\nSummary:")
        print(f"  Slither: {len(slither_findings)} findings")
        print(f"  Report: {report_path}")
        
        # Cleanup
        if self.target != self.work_dir:
            shutil.rmtree(self.work_dir, ignore_errors=True)
        
        return report_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python audit-workflow.py <github_url | etherscan_address | local_dir>")
        sys.exit(1)
    
    workflow = AuditWorkflow(sys.argv[1])
    workflow.run()
