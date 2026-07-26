#!/usr/bin/env python3
"""
On-Chain Anomaly Detector — RPC-based exploit scanner
Scans recent blocks for suspicious transaction patterns
Author: Shiqiang Chen · July 2026
"""

import json, subprocess, time, sys

RPC = "https://1rpc.io/eth"

def call(method, params):
    payload = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":1})
    try:
        out = subprocess.run(["curl","-s","-X","POST",RPC,
            "-H","Content-Type: application/json","-d",payload,
            "--connect-timeout","5"], capture_output=True, text=True, timeout=10)
        return json.loads(out.stdout)["result"]
    except: return None

def scan():
    print("🔍 On-Chain Anomaly Detector")
    print(f"   Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    block = call("eth_getBlockByNumber", ["latest", False])
    if not block:
        print("❌ RPC unavailable")
        return
    bn = int(block["number"], 16)
    print(f"   Block: {bn:,}")
    
    findings = []
    
    # Scan last 5 blocks
    for offset in range(5):
        target = hex(bn - offset)
        b = call("eth_getBlockByNumber", [target, False])
        if not b: continue
        
        for txh in b["transactions"][:30]:  # First 30 per block
            tx = call("eth_getTransactionByHash", [txh])
            if not tx: continue
            time.sleep(0.03)
            
            value = int(tx.get("value","0x0"),16) / 1e18
            to_addr = tx.get("to","")
            inp = tx.get("input","0x")
            gas_price = int(tx.get("gasPrice","0x0"),16) / 1e9
            gas_limit = int(tx.get("gas","0x0"),16) / 1e6
            
            # === Pattern 1: Large drain (>50 ETH) ===
            if value > 50:
                findings.append({
                    "type": "Large transfer", "amount": value,
                    "tx": txh, "block": bn - offset, "gas": gas_price
                })
            
            # === Pattern 2: Contract deployment (no 'to') ===
            if not to_addr:
                findings.append({
                    "type": "Contract deployment", 
                    "tx": txh, "block": bn - offset
                })
            
            # === Pattern 3: Very low gas (MEV relay) ===
            if gas_price < 2 and gas_limit > 0.5:
                findings.append({
                    "type": "MEV relay (low gas)", "gas": gas_price,
                    "tx": txh, "block": bn - offset
                })
            
            # === Pattern 4: Flash loan signature (large gas limit) ===
            if gas_limit > 5:
                findings.append({
                    "type": "Complex tx (>5M gas)", "gas": gas_limit,
                    "tx": txh, "block": bn - offset
                })
    
    if findings:
        print(f"\n⚠️  {len(findings)} anomalies found:")
        for f in findings[:15]:
            extra = ""
            if "amount" in f: extra = f" {f['amount']:.0f} ETH"
            if "gas" in f: extra = f" gas:{f['gas']:.1f}"
            print(f"  [{f['type']}] block {f['block']}{extra} | {f['tx'][:20]}...")
    else:
        print("✅ No anomalies in last 5 blocks")
    
    return findings

if __name__ == "__main__":
    scan()
