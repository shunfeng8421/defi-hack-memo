#!/usr/bin/env python3
"""
腿1 自动化扫描 — 依赖反查 + 信息泄露
每天一键跑，30分钟出结果
"""
import subprocess, json, os, datetime
from pathlib import Path

OUT = Path(r"C:\Users\Administrator\AppData\Local\Temp\daily-scan")
OUT.mkdir(exist_ok=True)

today = datetime.date.today().isoformat()
report_file = OUT / f"scan-{today}.md"
findings = []

def run(cmd, timeout=15):
    """Run shell command. Commands are hardcoded, no user input — safe."""
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)  # nosec — hardcoded commands only
    return r.stdout, r.stderr, r.returncode

def gh_search(query, label):
    """Search GitHub, return list of unique repos"""
    try:
        r = subprocess.run(
            ["gh", "api", f"search/code?q={query}&per_page=5"],
            capture_output=True, text=True, timeout=15
        )
        repos = []
        for item in json.loads(r.stdout).get("items", []):
            repo = item["repository"]["full_name"]
            path = item["path"]
            repos.append((repo, path))
        return repos
    except:
        return []

def check_bug_bounty(repo):
    """Check if a repo has a bug bounty on HackerOne (rough check)"""
    # This is a heuristic - can't perfectly detect bounty programs
    bounty_programs = {
        "portswigger", "internet archive", "proton", "brave", "mattermost",
        "gitlab", "elastic", "shopify", "uber", "square", "dropbox",
        "yahoo", "twitter", "linkedin", "paypal", "stripe", "netlify",
        "vercel", "nextcloud", "owncloud", "rocket.chat", "keybase",
        "semrush", "1password", "zoom", "okta", "auth0",
    }
    # Also check for disclosed vulnerabilities that might have bounties
    return repo.lower() in bounty_programs

print("=" * 60)
print("  腿1 — 每日漏洞扫描")
print(f"  日期: {today}")
print("=" * 60)

# ============================================================
# 1. Docker 老版本镜像
# ============================================================
print("\n[1/4] 扫描 Docker 老版本镜像...")

docker_queries = [
    # Langflow < 1.9.0
    ("langflow+1.7+OR+langflow+1.8+filename:docker-compose", "Langflow 老版本 (CVE-2026-33017 RCE)"),
    # Flowise < 3.1.3
    ("flowise+3.0+OR+flowise+3.1.0+OR+flowise+3.1.1+OR+flowise+3.1.2+filename:docker-compose", "Flowise 老版本 (RCE)"),
    # n8n < 1.110  (our CVE-2026-1470)
    ("n8n+1.100+OR+n8n+1.105+docker-compose", "n8n 老版本 (Sandbox Escape)"),
    # Kong < 2.1
    ("kong+2.0+docker-compose", "Kong 老版本 (Admin API RCE)"),
]

for query, label in docker_queries:
    repos = gh_search(query, label)
    for repo, path in repos:
        findings.append({
            "type": "OLD_VERSION",
            "label": label,
            "repo": repo,
            "path": path,
            "bounty": check_bug_bounty(repo),
        })
        bounty_flag = "💰 BOUNTY" if check_bug_bounty(repo) else "📋"
        print(f"  {bounty_flag} {repo} — {label}")
        print(f"      {path}")

# ============================================================
# 2. 泄露的 API Key
# ============================================================
print("\n[2/4] 扫描泄露的 API Key...")

key_queries = [
    "filename:.env+OPENAI_API_KEY+sk-",
    "filename:config+SECRET_KEY+%3D+%22+language:python+stars:>5",
    "filename:.env+AWS_SECRET_ACCESS_KEY",
]

for query in key_queries[:1]:  # limit to avoid rate limit
    try:
        r = subprocess.run(
            ["gh", "api", f"search/code?q={query}&per_page=3"],
            capture_output=True, text=True, timeout=15
        )
        for item in json.loads(r.stdout).get("items", []):
            repo = item["repository"]["full_name"]
            path = item["path"]
            findings.append({
                "type": "LEAKED_KEY",
                "label": "API Key 泄露",
                "repo": repo,
                "path": path,
                "bounty": False,
            })
            print(f"  🔑 {repo} — {path}")
    except:
        pass

# ============================================================
# 3. npm/PyPI 脆弱依赖
# ============================================================
print("\n[3/4] 扫描 npm 脆弱依赖...")

# Common vulnerable packages that still appear in deployments
vuln_packages = [
    ("lodash+4.17.19+OR+lodash+4.17.20+filename:package.json", "lodash 原型污染"),
    ("shell-quote+1.7+OR+shell-quote+1.8.0+OR+shell-quote+1.8.1+filename:package.json", "shell-quote 命令注入"),
]

for query, label in vuln_packages[:1]:
    try:
        r = subprocess.run(
            ["gh", "api", f"search/code?q={query}&per_page=3"],
            capture_output=True, text=True, timeout=15
        )
        for item in json.loads(r.stdout).get("items", []):
            repo = item["repository"]["full_name"]
            findings.append({
                "type": "VULN_DEP",
                "label": label,
                "repo": repo,
                "path": item["path"],
                "bounty": check_bug_bounty(repo),
            })
            bounty_flag = "💰" if check_bug_bounty(repo) else "📋"
            print(f"  {bounty_flag} {repo} — {label}")
    except:
        pass

# ============================================================
# 4. Exploit-DB RSS（今日新漏洞）
# ============================================================
print("\n[4/4] 检查 Exploit-DB 今日新漏洞...")

try:
    import urllib.request, re
    rss = urllib.request.urlopen("https://www.exploit-db.com/rss.xml", timeout=10).read().decode()
    titles = re.findall(r"<title>\[(.+?)\]\s+(.+?)</title>", rss)
    for cat, title in titles[:5]:
        if cat in ("webapps", "remote", "local"):
            print(f"  🔥 [{cat}] {title}")
except:
    print("  ⚠️ Exploit-DB 不可达")

# ============================================================
# 汇总报告
# ============================================================
print(f"\n{'='*60}")
print(f"  共发现 {len(findings)} 个潜在目标")
print(f"  Bug Bounty 赏金目标: {sum(1 for f in findings if f['bounty'])}")
print(f"{'='*60}")

# 写报告
with open(report_file, "w", encoding="utf-8") as f:
    f.write(f"# 每日扫描报告 — {today}\n\n")
    f.write(f"**总发现**: {len(findings)}\n")
    f.write(f"**可获赏金**: {sum(1 for f2 in findings if f2['bounty'])}\n\n")
    f.write("| 类型 | 项目 | 文件 | 赏金 |\n")
    f.write("|------|------|------|:--:|\n")
    for f2 in findings:
        bounty = "💰" if f2["bounty"] else "—"
        f.write(f"| {f2['type']} | {f2['repo']} | {f2['path']} | {bounty} |\n")

print(f"\n✅ 报告已保存: {report_file}")
