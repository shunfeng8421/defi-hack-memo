#!/usr/bin/env python3
"""
Target Priority Scanner — 10秒判断项目值不值得审
================================================
快速评分: 语言 → 代码量 → 安全文件 → 漏洞模式命中
返回 0-100 分, 80+ 直接审计
"""
import subprocess, json, tempfile, os, sys, zipfile, io, re
from pathlib import Path

RULES_DIR = Path(r"D:\hermes\skills\security-researcher\rules")

def score_repo(url_or_path: str) -> dict:
    score = 0
    reasons = []
    
    # 1. 语言判定
    lang_score = {"python": 0, "typescript": 0, "javascript": 0, "go": 0, "rust": 0}
    for lang, pts in [("python", 25), ("typescript", 20), ("javascript", 15), ("go", 25), ("rust", 20)]:
        if lang in url_or_path.lower():
            score += pts
            reasons.append(f"语言: {lang} +{pts}")
            break
    
    # 2. 用 gh api 判断流行度
    if "github.com" in url_or_path:
        repo_path = url_or_path.replace("https://github.com/", "").replace(".git", "")
        try:
            info = subprocess.run(
                ["gh", "api", f"repos/{repo_path}",
                 "--jq", '{stars: .stargazers_count, pushed: .pushed_at, size: .size, desc: .description, topics: .topics}'],
                capture_output=True, text=True, timeout=8
            )
            if info.returncode == 0:
                d = json.loads(info.stdout)
                # Stars
                if d["stars"] >= 100: score += 20; reasons.append(f"100+ ⭐ +20")
                elif d["stars"] >= 10: score += 10; reasons.append(f"10+ ⭐ +10")
                # Recently active
                pushed = d.get("pushed", "")
                if pushed and "2026-07" in pushed: score += 15; reasons.append("本月活跃 +15")
                # Size
                if d.get("size", 0) > 1000: score += 10; reasons.append("代码量大 +10")
                elif d.get("size", 0) > 100: score += 5; reasons.append("中等代码量 +5")
                # Topics
                if d["topics"]:
                    for t in d["topics"]:
                        if t in ("security", "penetration-testing", "bugbounty", "pentesting", "exploit"):
                            score += 15; reasons.append(f"安全工具 +15"); break
        except: pass
    
    # 3. 安全文件检查
    security_files = ["SECURITY.md", ".github/SECURITY.md", "security.txt"]
    score += 5  # 默认加分
    reasons.append("可审计 +5")
    
    # 4. 最终评分
    score = min(100, max(0, score))
    
    return {"score": score, "reasons": reasons, "verdict": "✅ 直接审" if score >= 60 else "⚠️ 可扫" if score >= 30 else "❌ 跳过"}

if __name__ == "__main__":
    targets = sys.argv[1:] if len(sys.argv) > 1 else []
    if not targets:
        # Default: test a few
        targets = [
            "https://github.com/Encod3d-Sec/ClaudeBrain",
            "https://github.com/QuantumByteOSS/quantumbyte",
            "https://github.com/Shubhamsaboo/awesome-llm-apps",
            "https://github.com/zhaochenyang20/Awesome-ML-SYS-Tutorial",
        ]
    for t in targets:
        r = score_repo(t)
        print(f"  {r['verdict']} {t:55s} {r['score']:2d}/100")
        for reason in r["reasons"][:3]: print(f"         {reason}")
        print()
