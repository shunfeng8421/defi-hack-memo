#!/usr/bin/env python3
"""Bridge Security Compliance Checker — CBSS v1.0"""
import sys

CHECKS = {
    1: "Message Verification — every incoming message format-validated?",
    2: "Validator Threshold — collusion-resistant? ≥2/3?",
    3: "Replay Protection — chainId+nonce+deadline in every message?",
    4: "Mint/Burn Invariant — cross-chain supply always balanced?",
    5: "Upgrade Safety — timelock + multi-sig on upgrade?",
    6: "Stuck Fund Recovery — failed delivery recovery path?",
}

LEVELS = {"🏆 Platinum": 6, "🥇 Gold": 5, "🥈 Silver": 4, "🥉 Bronze": 2}

def check(bridge: str, passed: list[int]):
    score = len(passed)
    print(f"\n{'='*50}")
    print(f"  CBSS Compliance Report — {bridge}")
    print(f"{'='*50}\n")
    for cid, desc in CHECKS.items():
        print(f"  {'✅' if cid in passed else '❌'} AS-{cid}: {desc}")
    level = "Unrated"
    for name, req in LEVELS.items():
        if score >= req: level = name; break
    print(f"\n  Score: {score}/6 | Level: {level}")
    return level

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Demo
        check("Cherum", [1,2,3,4,5])
        check("NomadBridge", [])
        check("PolyNetwork", [3])
        sys.exit(0)
    name = sys.argv[1]
    passed = [int(v) for v in sys.argv[2].split(",") if v.strip()] if len(sys.argv) > 2 and sys.argv[2].strip() else []
    check(name, passed)
