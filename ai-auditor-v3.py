#!/usr/bin/env python3
"""
AI Auditor v3.0 — Scanner + Structured Report
1. Clone repo → 2. Run 58-pattern scanner → 3. Parse JSON → 4. Generate report
Works without external LLM — produces structured output for Hermes analysis.
"""
import os, sys, json, subprocess, tempfile, re

SCANNER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "defi-scanner.py")

class AIAuditorV3:
    def __init__(self, target: str):
        self.target = target
        self.is_url = target.startswith(("http://", "https://", "git@"))

    def acquire(self) -> str:
        """Get source code — clone URL or use local path."""
        if self.is_url:
            workdir = tempfile.mkdtemp(prefix="audit_")
            subprocess.run(["git", "clone", "--depth", "1", "--quiet", self.target, workdir],
                          capture_output=True, timeout=60)
            return workdir
        return self.target

    def scan(self, path: str) -> dict:
        """Run 58-pattern scanner, return parsed JSON."""
        result = subprocess.run(
            [sys.executable, SCANNER, path],
            capture_output=True, text=True, timeout=120
        )
        # Find JSON output file
        json_path = os.path.join(path, "scan-results.json")
        if os.path.exists(json_path):
            with open(json_path) as f:
                return json.load(f)
        return {}

    def analyze(self, scan_data: dict) -> list:
        """Group findings by severity and pattern."""
        findings = []
        for filepath, items in scan_data.items():
            if not isinstance(items, list):
                continue
            for item in items:
                findings.append({
                    "file": os.path.basename(filepath),
                    "severity": item.get("severity", "?"),
                    "pattern": f"#{item.get('id', '?')}",
                    "name": item.get("name", "?"),
                    "description": item.get("description", ""),
                    "fix": item.get("fix", ""),
                    "lines": item.get("lines", [])
                })
        return sorted(findings, key=lambda f: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(f["severity"], 99))

    def report(self, findings: list, stats: dict) -> str:
        """Generate structured audit report."""
        severity_count = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for f in findings:
            severity_count[f["severity"]] += 1

        lines = [
            "# AI Auditor Report",
            f"\n**Target**: {self.target}",
            f"**Files**: {stats.get('files', '?')} | **Lines**: {stats.get('lines', '?')}",
            f"**Findings**: {sum(severity_count.values())} "
            f"(🔴{severity_count['CRITICAL']} 🟠{severity_count['HIGH']} 🟡{severity_count['MEDIUM']} 🔵{severity_count['LOW']})",
            "\n## Critical & High Findings\n"
        ]

        for f in findings:
            if f["severity"] in ("CRITICAL", "HIGH"):
                lines.append(
                    f"### {f['severity'][0]} {f['pattern']} {f['name']} — {f['file']}\n"
                    f"- **Issue**: {f['description']}\n"
                    f"- **Fix**: {f['fix']}\n"
                    f"- **Lines**: {', '.join(map(str, f['lines'][:3])) if f['lines'] else 'auto-detected'}\n"
                )
        return "\n".join(lines)

    def run(self):
        print(f"🔍 AI Auditor v3.0 — {self.target}\n")
        path = self.acquire()
        print(f"📂 Acquired: {path}")
        data = self.scan(path)
        stats = {"files": len(data), "lines": "?"}
        findings = self.analyze(data)
        report = self.report(findings, stats)
        out_path = os.path.join(path, "AI-AUDIT-REPORT.md")
        with open(out_path, "w") as f:
            f.write(report)
        print(report)
        print(f"\n📋 Report saved: {out_path}")
        return report

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="GitHub URL or local path")
    args = ap.parse_args()
    AIAuditorV3(args.target).run()
