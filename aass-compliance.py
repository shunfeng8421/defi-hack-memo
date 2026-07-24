#!/usr/bin/env python3
"""
AASS Compliance Checker — AI Agent Security Standard v1.0
Checks any protocol against 8 attack vectors.
"""
import sys

VECTORS = {
    1: "Tool Allowlist — can agent call any function?",
    2: "Contract Allowlist — can agent call any address?",
    3: "TWAP Oracle — spot price or 30min TWAP?",
    4: "MCP Encryption — is agent transport authenticated?",
    5: "Global Limits — per-wallet caps supersede per-agent?",
    6: "Agent Expiry — does agent authorization have duration?",
    7: "Risk Metric — reward function include loss prevention?",
    8: "Cumulative Confirm — daily total triggers re-auth?",
}

LEVELS = {"🥇 Gold": 8, "🥈 Silver": 5, "🥉 Bronze": 4}

def check(protocol: str, passed: list[int]) -> str:
    score = len(passed)
    
    print(f"\n{'='*50}")
    print(f"  AASS Compliance Report — {protocol}")
    print(f"{'='*50}\n")
    
    for vid, desc in VECTORS.items():
        status = "✅" if vid in passed else "❌"
        print(f"  {status} V{vid}: {desc}")
    
    level = "Unrated"
    for name, req in LEVELS.items():
        if score >= req:
            level = name; break
    
    print(f"\n  Score: {score}/8 | Level: {level}")
    return level

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python aass-compliance.py <protocol> <passed_vectors...>")
        print("Example: python aass-compliance.py SafeAIAgentWallet 1,2,3,5,6,8")
        sys.exit(1)
    
    name = sys.argv[1]
    passed = [int(v) for v in sys.argv[2].split(",") if v.strip()] if len(sys.argv) > 2 and sys.argv[2].strip() else []
    check(name, passed)

# Self-test
if __name__ == "__main__" and len(sys.argv) == 1:
    print("=== Self-Test: Safe AI Wallet ===")
    check("Safe AI Agent Wallet", [1, 2, 5, 6, 8])
    print("\n=== Self-Test: Swapper Finance ===")
    check("Swapper Finance", [])
