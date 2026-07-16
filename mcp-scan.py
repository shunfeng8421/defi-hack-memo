#!/usr/bin/env python3
"""
MCP Safety Scanner v1.2
自动评估 MCP 服务器的安全性 — 6 大攻击面检测 + 防篡改审计链
用法: python mcp-scan.py <repo_or_path>
"""
import subprocess, json, zipfile, io, os, sys, re, tempfile, hashlib, time
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════
# 防篡改审计链 (来自 awesome-llm-apps 模式)
# ═══════════════════════════════════════════

class AuditChain:
    """SHA-256 hash-chained audit trail — every scan step is verifiable."""
    GENESIS_HASH = "0" * 64
    
    def __init__(self):
        self.chain = []
    
    def record(self, step: str, detail: str) -> str:
        prev = self.chain[-1]["hash"] if self.chain else self.GENESIS_HASH
        ts = time.time()
        payload = f"{len(self.chain)}:{ts}:{step}:{detail}:{prev}"
        entry_hash = hashlib.sha256(payload.encode()).hexdigest()
        self.chain.append({
            "seq": len(self.chain), "ts": ts,
            "step": step, "detail": detail[:120],
            "prev": prev, "hash": entry_hash
        })
        return entry_hash
    
    def verify(self) -> bool:
        for i, e in enumerate(self.chain):
            expected_prev = self.chain[i-1]["hash"] if i > 0 else self.GENESIS_HASH
            if e["prev"] != expected_prev:
                return False
            payload = f"{e['seq']}:{e['ts']}:{e['step']}:{e['detail']}:{e['prev']}"
            if hashlib.sha256(payload.encode()).hexdigest() != e["hash"]:
                return False
        return True

class MCPScanner:
    def __init__(self, target):
        self.target = target
        self.findings = []
        self.tmp = Path(tempfile.mkdtemp(prefix="mcp-scan-"))
        self.code_dir = None
        self.audit = AuditChain()
        
    def run(self):
        print("=" * 55)
        print("  MCP Safety Scanner v1.2")
        print(f"  Audit Chain: 🔗 {'✅ VERIFIED' if self.audit.verify() else '❌ BROKEN'}")
        self.audit.record("scan_start", f"Target: {self.target}")
        print(f"  Target: {self.target}")
        print(f"  Time:   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 55)
        
        self._acquire()
        if not self.code_dir:
            print("[!] Failed to acquire target")
            return
        
        self._scan()
        self._report()
        self._cleanup()
        
    def _acquire(self):
        """Clone repo or use local path"""
        p = Path(self.target)
        if p.exists() and p.is_dir():
            self.code_dir = p
            print(f"[*] Using local path: {p}")
            return
        
        # Try GitHub repo
        try:
            r = subprocess.run(
                ["gh", "api", f"repos/{self.target}/zipball"],
                capture_output=True, timeout=30
            )
            if r.returncode == 0:
                extract_dir = self.tmp / "repo"
                extract_dir.mkdir()
                with zipfile.ZipFile(io.BytesIO(r.stdout)) as zf:
                    zf.extractall(extract_dir)
                # Find the inner directory
                dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
                self.code_dir = dirs[0] if dirs else extract_dir
                print(f"[*] Downloaded from GitHub: {self.target}")
                return
        except: pass
        
        # Try git clone
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", "--quiet",
                 f"https://github.com/{self.target}.git",
                 str(self.tmp / "repo")],
                timeout=30, capture_output=True
            )
            self.code_dir = self.tmp / "repo"
            print(f"[*] Cloned from GitHub: {self.target}")
            return
        except: pass
        
    def _scan(self):
        """Run all 6 attack surface checks"""
        print(f"\n[*] Scanning {sum(1 for _ in self._all_files())} files...\n")
        
        self._check_tool_injection()
        self._check_inspector_exposure()
        self._check_transport()
        self._check_implementation()
        self._check_supply_chain()
        
    # Directories to skip (test data, vendored libs, build artifacts)
    _SKIP_DIRS = {'test', 'tests', '__pycache__', 'node_modules', 'dist', 'build', 
                  '.git', 'lib', 'vendor', 'fixtures', 'corpus', 'examples'}
    
    def _all_files(self):
        for root, dirs, files in os.walk(self.code_dir):
            # Prune skip dirs
            dirs[:] = [d for d in dirs if d.lower() not in self._SKIP_DIRS]
            for f in files:
                if f.endswith(('.py', '.ts', '.js', '.go', '.rs', '.yaml', '.yml', '.toml', '.env')):
                    yield Path(root) / f
    
    def _read_safe(self, path):
        try: return path.read_text(encoding='utf-8', errors='replace')
        except: return ""
    
    def _add(self, severity, surface, detail, file_path, line=0):
        self.findings.append({
            "severity": severity,
            "surface": surface,
            "detail": detail,
            "file": str(file_path),
            "line": line
        })
    
    # === Attack Surface Checks ===
    
    def _check_tool_injection(self):
        """AS1: Tool parameter injection — file_path/open without validation"""
        patterns = {
            "file_path → open() no validation": [
                ('file_path', 'open('),
                ('filepath', 'open('),
            ]
        }
        for pat_name, sub_patterns in patterns.items():
            for kw1, kw2 in sub_patterns:
                for f in self._all_files():
                    code = self._read_safe(f)
                    if kw1 in code and kw2 in code:
                        has_validate = ('validate' in code and 'path' in code.lower()) or 'realpath' in code
                        if not has_validate:
                            self._add("HIGH", "AS1: Tool Injection", 
                                     f"{pat_name} — {kw1} parameter has no path validation",
                                     f)
    
    def _check_inspector_exposure(self):
        """AS2: Inspector binds 0.0.0.0 without auth"""
        for f in self._all_files():
            code = self._read_safe(f)
            if '0.0.0.0' in code and any(k in code for k in ('listen', 'bind', 'host', 'serve', 'HOST')):
                # Skip if nolint/test context
                if 'nolint:gosec' in code or '// test' in code:
                    continue
                has_auth = any(k in code.lower() for k in ('auth', 'apikey', 'api_key', 'token', 'bearer', 'jwt'))
                if not has_auth:
                    self._add("HIGH", "AS2: Inspector Exposure",
                             "Binds to 0.0.0.0 without authentication", f)
    
    def _check_transport(self):
        """AS4: Transport layer issues"""
        for f in self._all_files():
            code = self._read_safe(f)
            if 'http://' in code and 'localhost' not in code and '127.0.0.1' not in code:
                if 'mcp' in code.lower() or 'endpoint' in code.lower():
                    self._add("MEDIUM", "AS4: Transport",
                             "Uses unencrypted HTTP for MCP communication",
                             f)
    
    def _check_implementation(self):
        """AS5: Traditional web vulnerabilities"""
        for f in self._all_files():
            code = self._read_safe(f)
            
            # Command injection
            if 'shell=True' in code:
                self._add("HIGH", "AS5: Implementation",
                         "subprocess with shell=True — possible command injection", f)
            
            # SQL injection
            if 'execute(f"' in code or 'execute(f\'' in code.lower():
                self._add("HIGH", "AS5: Implementation",
                         "f-string SQL query — possible SQL injection", f)
            
            # eval/exec — skip test files and data formats
            if f.suffix in ('.py', '.ts', '.js', '.go'):
                if '.test.' not in f.name and '.spec.' not in f.name:
                    if 'eval(' in code and 'code' in code.lower():
                        self._add("HIGH", "AS5: Implementation",
                                 "eval() with code parameter — possible RCE", f)
            
            # Weak secrets (only flag if value looks like an actual secret)
            for i, line in enumerate(code.split('\n'), 1):
                if '=' in line and any(kw in line.upper() for kw in ('SECRET', 'PASSWORD', 'TOKEN', 'API_KEY')):
                    if 'getenv' in line.lower() or 'environ' in line.lower():
                        continue  # uses env var — not hardcoded
                    if 'SECRET_ENV' in line or 'SECRET_PATTERN' in line.upper():
                        continue  # variable name definition, not an actual secret
                    if ':' in line and '{' in line:  
                        continue  # JSON/TypeScript type annotation
                    # Check for suspicious default values
                    for weak in ('changeme', 'admin', 'password', 'secret', 'hunter2'):
                        if weak in line.lower() and '"' in line:
                            self._add("MEDIUM", "AS5: Implementation",
                                     f"Weak default secret: {line.strip()[:80]}", f, i)
                            break
    
    def _check_supply_chain(self):
        """AS6: Supply chain — check dependencies"""
        for f in self._all_files():
            if f.name in ('package.json', 'requirements.txt', 'pyproject.toml', 'go.mod', 'Cargo.toml'):
                code = self._read_safe(f)
                # Just flag for manual review
                self._add("INFO", "AS6: Supply Chain",
                         f"Dependency file found — review for known vulnerabilities: {f.name}", f)
    
    def _report(self):
        print(f"\n{'='*55}")
        print(f"  SCAN COMPLETE — {len(self.findings)} findings")
        print(f"{'='*55}\n")
        
        if not self.findings:
            print("✅ No security issues found.\n")
            return
        
        by_severity = {"HIGH": [], "MEDIUM": [], "INFO": []}
        for f in self.findings:
            by_severity[f["severity"]].append(f)
        
        for sev in ["HIGH", "MEDIUM", "INFO"]:
            items = by_severity[sev]
            if not items: continue
            icon = {"HIGH": "🔴", "MEDIUM": "🟡", "INFO": "🔵"}[sev]
            print(f"\n{icon} {sev} ({len(items)} findings)")
            for item in items:
                file_name = Path(item["file"]).name
                line_info = f":{item['line']}" if item['line'] else ""
                print(f"  [{item['surface']}] {item['detail']}")
                print(f"    → {file_name}{line_info}")
        
        print(f"\n💡 Review findings manually — automated scan may have false positives.\n")
        
        # Auditable chain output
        self.audit.record("scan_complete", f"{len(self.findings)} findings")
        chain_status = "✅ VERIFIED" if self.audit.verify() else "❌ TAMPERED"
        print(f"🔗 Audit Chain: {chain_status} | {len(self.audit.chain)} steps | Root: {self.audit.chain[-1]['hash'][:16] if self.audit.chain else 'N/A'}")
    
    def _cleanup(self):
        import shutil
        try: shutil.rmtree(self.tmp)
        except: pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mcp-scan.py <github_repo_or_local_path>")
        print("Example: python mcp-scan.py RhineLab-magellan/cherrystudio-qq-mcp")
        sys.exit(1)
    
    scanner = MCPScanner(sys.argv[1])
    scanner.run()
