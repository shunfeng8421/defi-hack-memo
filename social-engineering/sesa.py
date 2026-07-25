#!/usr/bin/env python3
"""
Social Engineering Security Assessment (SESA) v1.0
Evaluate protocol/personal vulnerability to the 6 most common crypto social engineering attacks.
Author: Shiqiang Chen · July 2026
"""

import sys, json
from collections import defaultdict

# ============================================================
# The Six Attack Vectors
# ============================================================
# Every major DeFi exploit >$100M had a human component:
#   Ronin $625M    — Fake job interview → engineer compromised
#   PolyNetwork    — "URGENT: upgrade needed" social pressure
#   Nomad $152M    — Rushed upgrade, bypassed review
#   Wormhole $326M — Missed patch notification from Solana

QUESTIONS = {
    "impersonation": {
        "weight": 25,
        "name": "Discord/Telegram Impersonation",
        "real_case": "Multiple DeFi hacks via fake admin accounts",
        "items": [
            ("All protocol actions require on-chain governance or multi-sig?",
             "yes_no", {"yes": 0, "no": 25}, 25),
            ("Is there a documented policy: 'NO action via Discord DM or Telegram'?",
             "yes_no", {"yes": 0, "no": 15}, 15),
            ("Are admin roles in Discord/Telegram verified by on-chain identity?",
             "yes_no", {"yes": 0, "no": 10}, 10),
            ("Do team members know: NEVER execute code from DM links?",
             "yes_no", {"yes": 0, "no": 20}, 20),
        ]
    },
    "social_recruitment": {
        "weight": 25,
        "name": "Fake Job Interview / Recruitment",
        "real_case": "Ronin Bridge $625M — engineer compromised via fake job offer",
        "items": [
            ("Do development machines have access to production signing keys?",
             "yes_no", {"yes": 25, "no": 0}, 25),
            ("Are all production operations done via hardware wallet?",
             "yes_no", {"no": 25, "yes": 0}, 25),
            ("Is there a process to verify recruiter identity before any technical test?",
             "yes_no", {"no": 15, "yes": 0}, 15),
        ]
    },
    "urgent_upgrade": {
        "weight": 20,
        "name": "Urgent Upgrade Social Pressure",
        "real_case": "Nomad Bridge $152M — rushed feature addition bypassed review",
        "items": [
            ("Is there a mandatory 48h timelock on ALL upgrades (no exceptions)?",
             "yes_no", {"no": 20, "yes": 0}, 20),
            ("Is there a policy: 'No emergency bypass of security review'?",
             "yes_no", {"no": 15, "yes": 0}, 15),
            ("Are upgrades approved by 2+ independent reviewers?",
             "yes_no", {"no": 10, "yes": 0}, 10),
        ]
    },
    "insider": {
        "weight": 15,
        "name": "Insider Threat",
        "real_case": "Multiple exchange hacks involved insiders",
        "items": [
            ("Can a single person deploy contracts or approve upgrades?",
             "yes_no", {"yes": 15, "no": 0}, 15),
            ("Are access permissions time-limited and automatically revocable?",
             "yes_no", {"no": 10, "yes": 0}, 10),
            ("Are production keys stored in geographically separated locations?",
             "yes_no", {"no": 5, "yes": 0}, 5),
        ]
    },
    "phishing": {
        "weight": 10,
        "name": "Phishing Contract Deployment",
        "real_case": "Fake Uniswap/AAVE contracts draining approved wallets",
        "items": [
            ("Does your protocol use ENS for contract address verification?",
             "yes_no", {"no": 5, "yes": 0}, 5),
            ("Are official contract addresses published in multiple independent channels?",
             "yes_no", {"no": 5, "yes": 0}, 5),
        ]
    },
    "bribery": {
        "weight": 5,
        "name": "Guardian/Validator Bribery",
        "real_case": "Governance attacks via token holder bribery",
        "items": [
            ("Do multi-sig signers have organizational diversity?",
             "yes_no", {"no": 5, "yes": 0}, 5),
            ("Do signers have public reputation at stake?",
             "yes_no", {"no": 3, "yes": 0}, 3),
        ]
    },
}

def assess():
    print("=" * 60)
    print("  Social Engineering Security Assessment (SESA) v1.0")
    print("=" * 60)
    print()
    print("This tool evaluates your protocol's vulnerability to the 6 most")
    print("common social engineering attack vectors in crypto.\n")
    print("For each question, answer: yes / no / n/a\n")
    
    results = {}
    total = 0
    max_total = 0
    
    for vector_id, vector in QUESTIONS.items():
        print(f"\n{'─' * 50}")
        print(f"  {vector['name']} (weight: {vector['weight']}%)")
        print(f"  Real case: {vector['real_case']}")
        print(f"{'─' * 50}\n")
        
        vector_score = 0
        vector_max = 0
        
        for i, (question, qtype, options, max_score) in enumerate(vector['items'], 1):
            while True:
                answer = input(f"  [{i}] {question}\n      (yes/no/na) > ").strip().lower()
                if answer in ('yes', 'no', 'na', 'y', 'n'):
                    break
                print("      Please answer: yes, no, or na")
            
            answer = answer[0]  # y/n
            if answer == 'y':
                answer = 'yes'
            elif answer == 'n':
                answer = 'no'
            else:
                answer = 'na'
            
            score = options.get(answer, 0) if answer != 'na' else 0
            vector_score += score
            vector_max += max_score
        
        risk = (vector_score / max(vector_max, 1)) * 100
        results[vector_id] = {
            "score": vector_score,
            "max": vector_max,
            "risk_pct": risk,
            "name": vector['name']
        }
        total += vector_score
        max_total += vector_max
    
    # Overall assessment
    overall = (total / max(max_total, 1)) * 100
    
    print(f"\n\n{'=' * 60}")
    print(f"  ASSESSMENT RESULTS")
    print(f"{'=' * 60}\n")
    
    if overall <= 20:
        grade = "🟢 LOW RISK — Strong social engineering defenses"
    elif overall <= 50:
        grade = "🟡 MODERATE RISK — Several weak points need attention"
    elif overall <= 75:
        grade = "🟠 HIGH RISK — Multiple critical gaps"
    else:
        grade = "🔴 CRITICAL RISK — Social engineering attack is probable"
    
    print(f"  Overall Score: {total}/{max_total} ({overall:.0f}%)")
    print(f"  Assessment: {grade}\n")
    
    print(f"  {'Vector':<35} {'Score':>6} {'Risk':>6}")
    print(f"  {'─' * 35} {'─' * 6} {'─' * 6}")
    for vid in sorted(results, key=lambda x: results[x]['risk_pct'], reverse=True):
        r = results[vid]
        bar = '█' * int(r['risk_pct'] / 10)
        print(f"  {r['name']:<35} {r['score']:>3}/{r['max']:<3} {bar}")
    
    print(f"\n  {'─' * 50}")
    print(f"  TOP 3 ACTIONS TO IMPROVE:")
    
    # Find top 3 issues
    issues = []
    for vid, vector in QUESTIONS.items():
        for question, qtype, options, max_score in vector['items']:
            # If the "yes" answer gives a high score = vulnerability exists
            if options.get('yes', 0) > 0:
                issues.append((options['yes'], question, max_score))
    issues.sort(reverse=True, key=lambda x: x[0])
    
    for i, (score, question, _) in enumerate(issues[:3], 1):
        print(f"  {i}. {question}")
    
    print(f"\n  {'─' * 50}")
    print(f"  REAL CASE COMPARISON:")
    print(f"  Ronin Bridge was vulnerable to: Fake Job Interview")
    print(f"  Nomad Bridge was vulnerable to: Urgent Upgrade Pressure")
    print(f"  Your protocol is MOST vulnerable to: {max(results, key=lambda x: results[x]['risk_pct'])}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Demo mode: show all questions without interaction
        print("SESA Demo — All vulnerabilities flagged for demonstration\n")
        for vid, vector in QUESTIONS.items():
            print(f"\n  {vector['name']}:")
            for q in vector['items']:
                print(f"    ❌ {q[0]}")
        print(f"\n  Total potential risk: 100%")
        print(f"  This is what an unsecured protocol looks like.")
    else:
        assess()
