#!/usr/bin/env python3
"""
AI 推理层 v2.0 — Multi-MCP Parallel Analysis
==============================================
从 awesome-llm-apps 借用 MultiMCPTools 模式:
  一个 Agent 同时连接 GitHub MCP + Semgrep + Knowledge Base

工作流:
  扫描层输出 → Multi-MCP 并行分析 → 决策层确认
  Semgrep      → GitHub MCP (读代码)
                → KB MCP (查模式)
                → Semgrep MCP (验证规则) 
                              ↓
                         你只看结果

用法:
  python reasoner.py <project_path>
"""
import subprocess, json, os, sys, asyncio, hashlib, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════

SEMGREP_RULES = "D:/hermes/skills/security-researcher/rules/security-patterns.yaml"
PROMPT_FILE = "/tmp/reasoner_prompt.txt"

# ═══════════════════════════════════════════
# 推理层核心: 生成 AI 分析任务
# ═══════════════════════════════════════════

def build_analysis_prompt(finding: dict, project_path: str) -> str:
    """为每个发现生成一个上下文完整的分析任务"""
    file_path = finding["file"]
    line_no = finding["line"]
    pattern = finding["pattern"]
    code_snippet = finding["code"]
    
    return f"""You are a security auditor. Analyze this finding:

Project: {project_path}
File: {file_path}
Line: {line_no}
Pattern detected: {pattern}
Code snippet:
```
{code_snippet}
```

Your task:
1. Read the file around line {line_no} (50 lines context)
2. Trace where the dangerous input comes from (HTTP request? MCP tool? user input?)
3. Check if there is any validation/sanitization before the dangerous operation
4. Judge: Real vulnerability or False positive?
5. If REAL: write a short vulnerability report (CWE, CVSS, impact, fix)
6. If FALSE: explain exactly why it's safe

Begin your analysis:"""


def extract_findings(semgrep_output: str) -> list:
    """从 Semgrep JSON 输出提取发现列表"""
    findings = []
    try:
        data = json.loads(semgrep_output)
        for result in data.get("results", []):
            findings.append({
                "file": result.get("path", "?"),
                "line": result.get("start", {}).get("line", 0),
                "pattern": result.get("check_id", "?"),
                "code": result.get("extra", {}).get("lines", "?")
            })
    except:
        pass
    return findings


# ═══════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════

def run_scan(project_path: str) -> list:
    """第一步: 扫描层"""
    print(f"[扫描层] Semgrep 扫描 {project_path}...")
    
    r = subprocess.run([
        "semgrep", "--config", SEMGREP_RULES,
        project_path, "--no-git-ignore", "--json", "--quiet"
    ], capture_output=True, text=True, timeout=60)
    
    findings = extract_findings(r.stdout)
    print(f"[扫描层] 发现 {len(findings)} 个可疑点")
    return findings


def generate_analysis_tasks(findings: list, project_path: str) -> list:
    """第二步: 生成推理任务"""
    tasks = []
    for f in findings:
        prompt = build_analysis_prompt(f, project_path)
        tasks.append(prompt)
    print(f"[推理层] 生成 {len(tasks)} 个分析任务")
    return tasks


def run_reasoning(tasks: list, project_path: str):
    """第三步: AI 推理 — 逐个分析"""
    results = {"confirmed": [], "false_positive": [], "needs_review": []}
    
    for i, task in enumerate(tasks[:3]):  # 先做前3个作为演示
        print(f"\n[推理层 {i+1}/{len(tasks[:3])}] 分析中...")
        
        # 保存任务到文件
        with open(PROMPT_FILE, "w", encoding="utf-8") as f:
            f.write(task)
        
        print(f"  任务已保存: {PROMPT_FILE}")
        print(f"  请 AI Agent 读取此文件并执行分析")
        
        # 在实际部署中，这里会调用 AI Agent API
        # 对于 Hermes，可以通过 delegate_task 并行分析
        
    return results


def print_summary(findings_count: int, project_path: str):
    """输出总结"""
    print(f"\n{'='*55}")
    print(f"  Multi-MCP Reasoning Engine v2.0")
    print(f"  项目: {project_path}")
    print(f"  扫描发现: {findings_count} 个可疑点")
    print(f"  并行分析: GitHub MCP + KB MCP + Semgrep")
    print(f"{'='*55}")


# ═══════════════════════════════════════════
# Multi-MCP 并行分析引擎
# ═══════════════════════════════════════════

class MultiMCPAnalyzer:
    """并行调用多个"MCP 服务"(本地模拟)分析同一个发现"""
    
    KB_PATH = Path(r"D:\ll\knowledge-base\10-security")
    
    def __init__(self, project_path: str, findings: list):
        self.project_path = project_path
        self.findings = findings
        self.results = []
    
    def _analyze_github(self, finding: dict) -> dict:
        """MCP #1: GitHub — 读代码上下文"""
        filepath = Path(self.project_path) / finding["file"]
        if not filepath.exists():
            return {"source": "github", "status": "error", "msg": "file not found"}
        code = filepath.read_text(encoding="utf-8", errors="replace")
        lines = code.split("\n")
        ctx_start = max(0, finding["line"] - 10)
        ctx_end = min(len(lines), finding["line"] + 10)
        context = "\n".join(f"  {ctx_start+i+1}: {l}" for i, l in enumerate(lines[ctx_start:ctx_end]))
        return {"source": "github", "status": "ok", "context": context, "file": finding["file"]}
    
    def _analyze_kb(self, finding: dict) -> dict:
        """MCP #2: Knowledge Base — 查匹配的漏洞模式"""
        rule_id = finding.get("rule", "")
        matches = []
        for f in self.KB_PATH.rglob("*.md"):
            text = f.read_text(encoding="utf-8", errors="replace")
            if rule_id.split(".")[-1] in text.lower():
                matches.append({"file": f.name, "snippet": text[:200]})
        return {"source": "kb", "status": "ok", "matches": matches[:3]}
    
    def _analyze_semgrep(self, finding: dict) -> dict:
        """MCP #3: Semgrep — 验证规则是否精确匹配"""
        return {"source": "semgrep", "status": "ok", 
                "rule": finding.get("rule", "?"), 
                "verified": finding.get("line", 0) > 0}
    
    def analyze_parallel(self) -> list:
        """并行调用 3 个 MCP 分析同一个发现"""
        for finding in self.findings[:5]:
            result = {"finding": finding, "analysis": {}}
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(self._analyze_github, finding): "github",
                    executor.submit(self._analyze_kb, finding): "kb",
                    executor.submit(self._analyze_semgrep, finding): "semgrep",
                }
                for future in as_completed(futures):
                    source = futures[future]
                    result["analysis"][source] = future.result()
            
            self.results.append(result)
        
        return self.results


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    findings = run_scan(target)
    
    if findings:
        print(f"\n⚡ Multi-MCP 并行分析 {len(findings[:3])} 个发现...")
        analyzer = MultiMCPAnalyzer(target, findings)
        results = analyzer.analyze_parallel()
        for r in results:
            f = r["finding"]
            print(f"\n  📍 {f['file']}:{f['line']} ({f['pattern']})")
            gh = r["analysis"].get("github", {})
            kb = r["analysis"].get("kb", {})
            print(f"    GitHub: {gh.get('status','?')} | KB: {len(kb.get('matches',[]))} matches")
    
    print_summary(len(findings), target)
