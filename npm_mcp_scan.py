#!/usr/bin/env python3
"""
npm MCP Batch Scanner — 批量审计整个 npm MCP 生态
==================================================
从 npm registry 拉取 MCP 包 → 运行 40 条 Semgrep 规则 → 记录发现

用法:
  python npm_mcp_scan.py           # 完整扫描
  python npm_mcp_scan.py --limit 20 # 测试 20 个包
"""
import subprocess, json, tempfile, os, sys, tarfile, io, re, time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request

SEMGREP_RULES = Path(r"D:\hermes\skills\security-researcher\rules")
SEMGREP_PYTHON = SEMGREP_RULES / "security-patterns.yaml"
SEMGREP_GO = SEMGREP_RULES / "go-rules.yaml"
SEMGREP_TS = SEMGREP_RULES / "ts-rules.yaml"
SEMGREP_RUST = SEMGREP_RULES / "rust-rules.yaml"
OUTPUT = Path(r"D:\ll\knowledge-base\10-security\findings")
SCAN_LOG = OUTPUT / f"npm-scan-{datetime.now().strftime('%Y%m%d-%H%M')}.jsonl"
SEEN_CACHE = OUTPUT / "npm-scan-seen.json"
OUTPUT.mkdir(parents=True, exist_ok=True)

def load_seen():
    if SEEN_CACHE.exists():
        return set(json.loads(SEEN_CACHE.read_text()))
    return set()

def save_seen(seen):
    SEEN_CACHE.write_text(json.dumps(list(seen)))

SEEN = load_seen()

def search_npm(query="mcp", max_packages=100, offset=0):
    """从 npm registry 搜索包——支持翻页"""
    packages = []
    page_size = min(max_packages, 250)
    pages_fetched = 0
    
    while len(packages) < max_packages and pages_fetched < 5:
        current_offset = offset + pages_fetched * page_size
        try:
            url = f"https://registry.npmjs.org/-/v1/search?text={query}&size={page_size}&from={current_offset}"
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
            new = data["total"] if "total" in data else 0
            for obj in data.get("objects", []):
                pkg = obj["package"]
                packages.append({
                    "name": pkg["name"],
                    "version": pkg.get("version","?"),
                    "description": (pkg.get("description","") or "")[:80],
                })
            pages_fetched += 1
            if len(data.get("objects",[])) < page_size:  # last page
                break
        except Exception as e:
            print(f"[!] npm search page {pages_fetched} failed: {e}")
            break
    return packages

def download_and_scan(pkg):
    """下载一个 npm 包 → 解压 → Semgrep 扫描 → 返回发现"""
    name = pkg["name"].replace("/", "-").replace("@", "")
    tmp = Path(tempfile.mkdtemp(prefix=f"npm-mcp-{name}-"))
    findings = []
    
    try:
        # 下载 tarball
        tarball_url = f"https://registry.npmjs.org/{pkg['name']}/-/{pkg['name'].split('/')[-1]}-{pkg['version']}.tgz"
        # 对 scoped package (@scope/name) 修正 URL
        if pkg["name"].startswith("@"):
            tarball_url = f"https://registry.npmjs.org/{pkg['name']}/-/{pkg['name'].split('/')[-1]}-{pkg['version']}.tgz"
        
        req = urllib.request.Request(tarball_url, headers={"Accept": "application/octet-stream"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        
        # 解压
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            tar.extractall(tmp)
        
        # 找源码目录
        src_dir = tmp
        for d in tmp.iterdir():
            if d.is_dir() and d.name == "package":
                src_dir = d
                break
        
        # 检测语言
        py_files = list(src_dir.rglob("*.py"))
        ts_files = list(src_dir.rglob("*.ts")) + list(src_dir.rglob("*.js"))
        go_files = list(src_dir.rglob("*.go"))
        rs_files = list(src_dir.rglob("*.rs"))
        
        rules_to_run = []
        if len(py_files) > 2:
            rules_to_run.append(("python", str(SEMGREP_PYTHON)))
        if len(ts_files) > 2:
            rules_to_run.append(("typescript", str(SEMGREP_TS)))
        if len(go_files) > 2:
            rules_to_run.append(("go", str(SEMGREP_GO)))
        if len(rs_files) > 2:
            rules_to_run.append(("rust", str(SEMGREP_RUST)))
        
        if not rules_to_run:
            return {"package": pkg["name"], "findings": 0, "languages": 0, "status": "no_code"}
        
        # 运行 Semgrep
        for lang, rules in rules_to_run:
            r = subprocess.run(
                ["semgrep", "--config", rules, str(src_dir), "--no-git-ignore", "--json", "--quiet"],
                capture_output=True, text=True, timeout=60
            )
            if r.returncode == 0:
                try:
                    semgrep_data = json.loads(r.stdout)
                    for result in semgrep_data.get("results", []):
                        findings.append({
                            "rule": result.get("check_id", "?"),
                            "file": result.get("path", "?"),
                            "line": result.get("start", {}).get("line", 0),
                            "language": lang
                        })
                except:
                    pass
        
        total = len(findings)
        if total > 0:
            # 写入日志
            entry = json.dumps({
                "package": pkg["name"],
                "version": pkg["version"],
                "findings": total,
                "details": findings[:10]
            }, ensure_ascii=False)
            with open(SCAN_LOG, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
    
    except Exception as e:
        return {"package": pkg["name"], "findings": 0, "status": "error", "error": str(e)[:80]}
    finally:
        import shutil
        try: shutil.rmtree(tmp)
        except: pass
    
    return {"package": pkg["name"], "findings": total, "languages": len(rules_to_run),
            "files": len(py_files)+len(ts_files)+len(go_files)+len(rs_files),
            "status": "done", "highlights": findings[:3]}


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    max_pkgs = limit or 100
    offset = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    query = sys.argv[3] if len(sys.argv) > 3 else "mcp"
    
    print(f"{'='*60}")
    print(f"  npm MCP Batch Scanner")
    print(f"  Query: '{query}', offset={offset}, max={max_pkgs}...")
    print(f"  Log: {SCAN_LOG}")
    print(f"{'='*60}\n")
    
    packages = search_npm(query, max_pkgs, offset)
    print(f"  Found {len(packages)} packages\n")
    
    # Focus on packages with potential MCP tools (file/browser/db operations)
    high_risk_keywords = ["filesystem","file","browser","playwright","puppeteer",
                         "sql","database","postgres","mysql","git","github",
                         "docker","server","s3","aws","kubernetes","shell","exec"]
    risky = [p for p in packages if any(kw in p["name"].lower() or kw in p.get("description","").lower() for kw in high_risk_keywords)]
    print(f"  Filtered {len(risky)} high-risk packages (file/db/browser ops)\n")
    
    scan_targets = risky[:max_pkgs]
    # Dedup: skip already scanned packages
    new_targets = [p for p in scan_targets if f"{p['name']}@{p['version']}" not in SEEN]
    if len(new_targets) < len(scan_targets):
        print(f"  Skipped {len(scan_targets) - len(new_targets)} already-scanned packages")
    scan_targets = new_targets
    total_findings = 0
    packages_with_findings = 0
    
    print(f"  Scanning {len(scan_targets)} packages with 4 workers...\n")
    
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(download_and_scan, p): p for p in scan_targets}
        done = 0
        for future in as_completed(futures):
            done += 1
            result = future.result()
            pkg = futures[future]
            status = "🔴" if result.get("findings",0) > 0 else "✅"
            err = f" | ⚠️ {result['status']}" if result.get("status") != "done" else ""
            print(f"  [{done:3d}/{len(scan_targets)}] {status} {pkg['name']:50s} "
                  f"{result.get('findings',0):2d} findings | {result.get('languages',0)} langs | "
                  f"{result.get('files',0)} files{err}")
            if result.get("findings",0) > 0:
                total_findings += result["findings"]
                packages_with_findings += 1
    
    # Record all scanned packages
    for p in scan_targets:
        SEEN.add(f"{p['name']}@{p['version']}")
    save_seen(SEEN)
    
    print(f"\n{'='*60}")
    print(f"  SCAN COMPLETE")
    print(f"  Packages: {done} | Found: {packages_with_findings} with issues")
    print(f"  Total findings: {total_findings}")
    print(f"  Log: {SCAN_LOG}")
    print(f"{'='*60}")
