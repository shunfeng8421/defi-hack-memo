#!/usr/bin/env python3
"""Master Security Scanner — DeFi 50 + AI Agent 8 = 58 Patterns"""
import os, sys, json, subprocess, tempfile

SCANNERS = {
    "defi": {
        "path": os.path.join(os.path.dirname(__file__), "defi-scanner.py"),
        "name": "DeFi 50-Pattern Scanner",
        "patterns": 50
    },
    "ai_agent": {
        "path": os.path.join(os.path.dirname(__file__), "ai-agent-scanner.py"),
        "name": "AI Agent 8-Vector Scanner",
        "patterns": 8
    }
}

def run_scanner(name: str, info: dict, target: str) -> dict:
    """Run a scanner and parse its JSON output."""
    result = {"name": info["name"], "findings": 0, "files": 0, "critical": 0, "high": 0}
    
    try:
        output = subprocess.run(
            ["python", info["path"], target],
            capture_output=True, text=True, timeout=60
        )
    except Exception as e:
        result["error"] = str(e)
        return result
    
    # Parse output for stats
    text = output.stdout + output.stderr
    for line in text.split('\n'):
        if 'Total' in line and 'findings' in line and not 'AI Agent' in line:
            import re
            m = re.search(r'(\d+)', line)
            if m: result["findings"] = int(m.group(1))
        if 'Files scanned' in line or 'file' in line.lower() and 'Scanned' in text:
            m = re.search(r'(\d+)', line)
            if m: result["files"] = int(m.group(1))
    
    # Count severity from output
    result["critical"] = text.count("CRITICAL")  # rough estimate
    result["high"] = text.count("HIGH")
    
    return result

def combined_scan(target: str):
    """Run both scanners and produce combined report."""
    print(f"\n{'='*70}")
    print(f"  🔐 MASTER SECURITY SCANNER")
    print(f"  DeFi 50 + AI Agent 8 = 58 Attack Patterns")
    print(f"  Author: Shiqiang Chen | github.com/shunfeng8421/defi-hack-memo")
    print(f"{'='*70}\n")
    
    results = {}
    for key, info in SCANNERS.items():
        print(f"  Running {info['name']}...")
        results[key] = run_scanner(key, info, target)
        r = results[key]
        status = "✅" if not r.get("error") else "❌"
        print(f"  {status} {r['findings']} findings in {r.get('files', '?')} files\n")
    
    # Combined stats
    total = sum(r["findings"] for r in results.values())
    total_crit = sum(r["critical"] for r in results.values())
    total_high = sum(r["high"] for r in results.values())
    
    print(f"{'='*70}")
    print(f"  📊 COMBINED REPORT")
    print(f"  {'='*70}")
    print(f"  Total findings  : {total}")
    print(f"  Critical/High   : {total_crit}/{total_high}")
    print(f"  Coverage        : 58 attack patterns (50 DeFi + 8 AI Agent)")
    print(f"  {'='*70}")
    print(f"  Scanners:")
    for key, r in results.items():
        icon = "✅" if not r.get("error") else "❌"
        print(f"    {icon} {SCANNERS[key]['name']}: {r['findings']} findings")
    print(f"  {'='*70}\n")
    
    # Save combined report
    combined = {
        "scanner": "Master Security Scanner v2.0",
        "author": "Shiqiang Chen",
        "patterns": 58,
        "results": results
    }
    out_path = os.path.join(target if os.path.isdir(target) else os.path.dirname(target), "master-scan.json")
    with open(out_path, 'w') as f:
        json.dump(combined, f, indent=2)
    print(f"  Report saved: {out_path}\n")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    combined_scan(target)
