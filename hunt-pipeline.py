#!/usr/bin/env python3
"""
Zero-Day Hunting Pipeline v1.0
Etherscan API → Download source → 58-pattern scan → Report
Author: Shiqiang Chen · July 2026
"""
import urllib.request, json, os, sys, tempfile, subprocess

ETHERSCAN_KEY = "DNVK62P3CZ5ACPQCN1XP47N57A7MBMW2J9"
PROXY = "http://127.0.0.1:15236"

# Setup proxy globally for urllib
proxy_handler = urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)

def etherscan_get(endpoint: str, params: dict) -> dict:
    """Query Etherscan V2 API through proxy."""
    params["apikey"] = ETHERSCAN_KEY
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"https://api.etherscan.io/v2/api?chainid=1&module={endpoint}&{qs}"
    
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())

def get_latest_verified_contracts(limit: int = 10) -> list:
    """Get recently verified contracts from Etherscan."""
    # Etherscan doesn't have a "recent verified" API directly,
    # so we use the block range approach: get latest block → scan backward
    params = {
        "module": "proxy",
        "action": "eth_blockNumber",
    }
    resp = etherscan_get("proxy", {"action": "eth_blockNumber"})
    latest_block = int(resp["result"], 16)
    
    # Check 20 blocks for contract creation
    contracts = []
    for block_num in range(latest_block, latest_block - 20, -1):
        block_hex = hex(block_num)
        resp = etherscan_get("proxy", {
            "action": "eth_getBlockByNumber",
            "tag": block_hex,
            "boolean": "true"
        })
        if "result" in resp and resp["result"]:
            for tx in resp["result"].get("transactions", []):
                if tx.get("to") is None:  # Contract creation
                    contracts.append({
                        "address": tx.get("creates", ""),
                        "block": block_num,
                        "from": tx.get("from", ""),
                    })
    return contracts

def download_source(address: str) -> dict:
    """Download verified source code for a contract."""
    resp = etherscan_get("contract", {
        "action": "getsourcecode",
        "address": address
    })
    if resp.get("status") == "1" and resp.get("result"):
        result = resp["result"][0]
        return {
            "name": result.get("ContractName", "Unknown"),
            "source": result.get("SourceCode", ""),
            "abi": result.get("ABI", "[]"),
            "compiler": result.get("CompilerVersion", ""),
        }
    return None

def scan_with_scanner(source_code: str, contract_name: str) -> list:
    """Run 58-pattern scanner on downloaded source."""
    # Write to temp file
    tmpdir = tempfile.mkdtemp()
    filepath = os.path.join(tmpdir, f"{contract_name}.sol")
    with open(filepath, "w") as f:
        f.write(source_code)
    
    # Run scanner
    scanner = os.path.join(os.path.dirname(__file__), "defi-scanner.py")
    result = subprocess.run(
        ["python", scanner, tmpdir],
        capture_output=True, text=True, timeout=30
    )
    
    # Parse findings
    findings = []
    for line in result.stdout.split("\n"):
        if any(emoji in line for emoji in ["🔴", "🟠", "🟡"]):
            findings.append(line.strip())
    
    return findings

if __name__ == "__main__":
    print("=" * 60)
    print("  Zero-Day Hunting Pipeline")
    print("=" * 60)
    print()
    
    print("[1] Finding recent contract deployments...")
    contracts = get_latest_verified_contracts(10)
    print(f"    Found {len(contracts)} recently deployed contracts")
    
    print("\n[2] Downloading source and scanning...")
    targets_found = 0
    for contract in contracts[:5]:
        addr = contract.get("address", "")
        if not addr:
            continue
        source = download_source(addr)
        if source:
            findings = scan_with_scanner(source["source"], source["name"])
            cr = sum(1 for f in findings if "CRITICAL" in f)
            hi = sum(1 for f in findings if "HIGH" in f)
            if cr + hi > 0:
                print(f"\n  🔍 {source['name']} ({addr[:10]}...)")
                print(f"     🔴{cr} 🟠{hi} — {len(findings)} total")
                targets_found += 1
                if targets_found >= 3:
                    break
    
    print(f"\n[3] Pipeline complete. {targets_found} targets worth investigating.")
