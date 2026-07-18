#!/usr/bin/env python3
"""AI Agent × DeFi Security Scanner — 8-Vector Detection"""
import os, re, json, sys

VECTORS = {
    1: {
        "name": "Tool Instruction Injection",
        "severity": "CRITICAL",
        "patterns": [
            (r'function execute\w*\(string.*tool|function run\w*\(string.*command', "Dynamic tool dispatch"),
            (r'delegatecall\(|\.call\(abi\.encodeWithSignature', "Arbitrary external call"),
            (r'^\s*(?!.*whitelist).*execute.*\(.*string.*,.*bytes', "No tool whitelist"),
        ],
        "fix": "Whitelist tool names; validate tool output before state changes"
    },
    2: {
        "name": "Cross-Contract Auto-DeFi Chain",
        "severity": "HIGH",
        "patterns": [
            (r'approve\([^)]*type\(uint256\)\.max|approve\([^)]*unlimited', "Unlimited approval"),
            (r'function.*auto.*\w+.*deposit|function.*auto.*\w+.*trade', "Auto-execute path"),
            (r'(approve|transfer|deposit).*\n.*\n.*(swap|deposit|borrow)', "Multi-step chain"),
        ],
        "fix": "Per-trade spending cap; multi-tx timeout; ReentrancyGuard"
    },
    3: {
        "name": "Oracle Data Poisoning (AI Decision)",
        "severity": "HIGH",
        "patterns": [
            (r'getReserves\(\)(?!.*TWAP)|globalState\(\)(?!.*TWAP)', "Spot price without TWAP"),
            (r'getSpotPrice|instantPrice|currentPrice', "Spot/instant price naming"),
            (r'supplyRate|borrowRate|getAPY|getYield', "On-chain yield metric"),
        ],
        "fix": "TWAP minimum 30min; multi-source median; deviation check"
    },
    4: {
        "name": "MCP/Registry Man-in-the-Middle",
        "severity": "CRITICAL",
        "patterns": [
            (r'mapping.*=>.*reputation|mapping.*=>.*trustScore', "On-chain trust score"),
            (r'mock.*reputation|placeholder.*registry|TODO.*ERC.?8004', "Mock/placeholder registry"),
            (r'function.*get[A-Z]\w*\(.*\).*view.*returns', "Unverified external data read"),
        ],
        "fix": "TLS verification; signature on all responses; deviation alerts"
    },
    5: {
        "name": "AI Decision Timing Window",
        "severity": "MEDIUM",
        "patterns": [
            (r'function\s+\w+close\w*\s*\([^)]*\)\s*external(?!.*only\w+)', "Permissionless close"),
            (r'function\s+\w+liquidat\w*\s*\([^)]*\)\s*external(?!.*only\w+)', "Permissionless liquidation"),
            (r'block\.(number|timestamp)\s*[><]', "Block/time dependency"),
        ],
        "fix": "Commit-reveal; priority window for agent; MEV protection"
    },
    6: {
        "name": "Multi-Agent Collusion Surface",
        "severity": "MEDIUM",
        "patterns": [
            (r'recoveryScore|reputation|ranking|leaderboard', "Ranking system"),
            (r'selectFallback|pickWinner|chooseAgent', "Agent selection algorithm"),
            (r'successRate|completedTasks|totalEarnings', "Accumulated metrics"),
        ],
        "fix": "Sybil-resistant identity; stake slashing for collusion; randomized selection"
    },
    7: {
        "name": "Context Memory Poisoning",
        "severity": "MEDIUM",
        "patterns": [
            (r'trustScore|confidence|belief', "Persistent trust state"),
            (r'mapping\(address\s*=>.*Score|mapping\(address\s*=>.*Rate', "Score mapping"),
            (r'function.*build\w*trust|function.*update\w*trust', "Trust update function"),
        ],
        "fix": "Memory decay over time; only accept on-chain verified data"
    },
    8: {
        "name": "Autonomous Signing Theft",
        "severity": "CRITICAL",
        "patterns": [
            (r'function\s+sign\w*\s*\(|_signTypedData|signMessage', "Autonomous signing"),
            (r'controller|delegate\w*\(.*agent|setController', "Agent delegation"),
            (r'^(?!.*maxNotional).*agent.*trade|^(?!.*expir).*agent.*execute', "Unbounded agent authority"),
        ],
        "fix": "Per-trade notional cap; expiry; human confirmation for large amounts"
    },
}

def scan_file(filepath: str) -> list:
    with open(filepath, encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    findings = []
    for vid, vec in VECTORS.items():
        for pattern, desc in vec["patterns"]:
            matches = []
            for line_no, line in enumerate(content.split('\n'), 1):
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append(line_no)
            if matches:
                findings.append({
                    "id": vid,
                    "name": vec["name"],
                    "severity": vec["severity"],
                    "description": desc,
                    "fix": vec["fix"],
                    "lines": matches[:3]
                })
    return findings

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    all_findings = {}
    file_count = 0
    
    if os.path.isfile(target):
        all_findings[target] = scan_file(target)
        file_count = 1
    else:
        for root, _, files in os.walk(target):
            for f in files:
                if not f.endswith('.sol'): continue
                path = os.path.join(root, f)
                findings = scan_file(path)
                if findings:
                    all_findings[path] = findings
                    file_count += 1
    
    print(f"\n🤖 AI Agent × DeFi Security Scan")
    print(f"   Scanned {file_count} Solidity files")
    print(f"   Detecting 8 AI Agent attack vectors\n")
    
    total = 0
    for path, findings in sorted(all_findings.items()):
        name = os.path.basename(path)
        for f in findings:
            total += 1
            icon = "🔴" if f["severity"]=="CRITICAL" else "🟠" if f["severity"]=="HIGH" else "🟡"
            print(f"  {icon} [{f['id']}] {f['name']}")
            print(f"      File: {name}:{','.join(map(str,f['lines'][:3]))}")
            print(f"      {f['description']}")
            print(f"      Fix: {f['fix']}\n")
    
    print(f"{'='*60}")
    print(f"Total AI Agent attack surface findings: {total} across {file_count} files")
    
    # Save JSON
    out = os.path.join(os.path.dirname(target) if os.path.isfile(target) else target, "ai-agent-scan.json")
    with open(out, 'w') as f:
        json.dump(all_findings, f, indent=2, default=str)
    print(f"JSON: {out}")
