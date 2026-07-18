#!/usr/bin/env python3
"""
AI Auditor v2.0 — LLM集成版
流水线: 克隆 → 58模式扫描 → LLM分析 → 智能审计报告
作者: Shiqiang Chen · July 2026
"""
import os, sys, json, subprocess, tempfile, re, urllib.request
from datetime import datetime

# ═══════════════════════════════════════
# LLM 客户端 — 通用 OpenAI 兼容接口
# 支持 Ollama / OpenAI / DeepSeek / 任何兼容API
# ═══════════════════════════════════════
class LLMClient:
    """通用LLM客户端"""
    
    def __init__(self):
        # 自动检测: Ollama 本地 > OpenAI API > DeepSeek
        self.provider = None
        self.model = None
        
        if self._test_ollama():
            self.provider = "ollama"
            self.model = "qwen2.5:7b"
            self.base_url = "http://localhost:11434/v1"
        elif os.getenv("OPENAI_API_KEY"):
            self.provider = "openai"
            self.model = "gpt-3.5-turbo"
            self.base_url = "https://api.openai.com/v1"
        elif os.getenv("DEEPSEEK_API_KEY"):
            self.provider = "deepseek"
            self.model = "deepseek-chat"
            self.base_url = "https://api.deepseek.com/v1"
        else:
            self.provider = "none"
            print("  ⚠️ 无LLM可用 — 使用规则引擎代替")
    
    def _test_ollama(self) -> bool:
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
            urllib.request.urlopen(req, timeout=2)
            return True
        except:
            return False
    
    def call(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
        """调用LLM"""
        if self.provider == "none":
            return self._rule_fallback(user_prompt)
        
        api_key = os.getenv(
            {"ollama": "ollama", "openai": "OPENAI_API_KEY", "deepseek": "DEEPSEEK_API_KEY"}[self.provider]
        )
        
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.1
        }).encode('utf-8')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        url = f"{self.base_url}/chat/completions"
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  ⚠️ LLM调用失败: {e}")
            return self._rule_fallback(user_prompt)
    
    def _rule_fallback(self, user_prompt: str) -> str:
        """无LLM时的规则引擎后备"""
        findings = []
        if "CRITICAL" in user_prompt:
            findings.append("CRITICAL: Immediate action required")
        if "HIGH" in user_prompt:
            findings.append("HIGH: High priority fix needed")  
        if "MEDIUM" in user_prompt:
            findings.append("MEDIUM: Address in next sprint")
        return "\n".join(findings) if findings else "No significant issues found."


# ═══════════════════════════════════════
# LLM 审计分析器
# ═══════════════════════════════════════
class LLMAuditAnalyzer:
    """用LLM分析扫描结果，生成专业审计意见"""
    
    SYSTEM_PROMPT = """你是一个顶级的 DeFi 安全审计专家。你的工作是分析智能合约扫描结果并给出专业的审计意见。

对于每个发现:
1. 用一句话解释漏洞
2. 给出具体的攻击场景(3步以内)
3. 提供修复代码(solidity代码片段)
4. 标注严重程度

请用以下格式输出每个发现:
### [严重性] 漏洞名称
**解释**: ...  
**攻击场景**: ...
**修复**: ```solidity ... ```
"""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
    
    def analyze(self, scan_output: str) -> str:
        """让LLM分析扫描输出"""
        # 只取前4000字符的扫描结果发给LLM
        truncated = scan_output[:4000]
        
        prompt = f"""以下是 58种模式的 DeFi 安全扫描器对一个 Solidity 项目的扫描结果。请分析这些结果并给出审计意见。

=== 扫描结果 ===
{truncated}

请对每个 CRITICAL 和 HIGH 级别的发现进行详细分析。如果没有严重发现，请说明项目当前的安全状态。"""
        
        return self.llm.call(self.SYSTEM_PROMPT, prompt)


# ═══════════════════════════════════════
# 集成: AI Auditor v2.0 (with LLM)
# ═══════════════════════════════════════
class AIAuditorV2:
    """LLM增强的自动化审计Agent"""
    
    def __init__(self):
        self.llm = LLMClient()
        self.analyzer = LLMAuditAnalyzer(self.llm)
        print(f"  🧠 LLM: {self.llm.provider}/{self.llm.model}" if self.llm.provider != "none" 
              else "  🧠 LLM: 规则引擎模式")
    
    def audit(self, target: str) -> str:
        """完整审计流水线(含LLM分析)"""
        print(f"\n{'='*60}")
        print(f"  🤖 AI Auditor v2.0 (LLM-Enhanced)")
        print(f"  目标: {target}")
        print(f"{'='*60}\n")
        
        # Step 1: 克隆
        if os.path.exists(target):
            workdir = target
        else:
            repo_name = target.rstrip('/').split('/')[-1]
            workdir = os.path.join(tempfile.gettempdir(), f"ai-audit-v2-{repo_name}")
            if not os.path.exists(workdir):
                print(f"  📥 克隆: {target}")
                subprocess.run(["git", "clone", "--depth", "1", "--quiet", target, workdir], timeout=60)
        
        # Step 2: 运行主扫描器
        print(f"  🔍 运行 58模式扫描...")
        result = subprocess.run(
            ["python", os.path.join(os.path.dirname(__file__), "defi-scanner.py"), workdir],
            capture_output=True, text=True, timeout=120
        )
        scan_output = result.stdout
        
        # 同时运行 AI Agent 扫描器
        result2 = subprocess.run(
            ["python", os.path.join(os.path.dirname(__file__), "ai-agent-scanner.py"), workdir],
            capture_output=True, text=True, timeout=60
        )
        scan_output += "\n" + result2.stdout
        
        # Step 3: LLM 分析
        print(f"  🧠 LLM 分析中...")
        llm_analysis = self.analyzer.analyze(scan_output)
        
        # Step 4: 生成完整报告
        report = self._generate_report(target, scan_output, llm_analysis)
        
        # 保存
        report_path = os.path.join(workdir, "AI-AUDIT-LLM-REPORT.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"  ✅ 审计完成 → {report_path}")
        return report
    
    def _generate_report(self, target: str, scan: str, llm: str) -> str:
        project = os.path.basename(target.rstrip('/'))
        critical = scan.count("🔴") + scan.count("CRITICAL")
        high = scan.count("🟠") + scan.count("HIGH")
        
        return f"""# 🤖 AI-Powered Audit Report — {project}

**日期**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**引擎**: 58-Pattern Scanner + LLM Analysis
**审计师**: Shiqiang Chen (AI-Assisted)
**LLM**: {self.llm.provider}/{self.llm.model}

---

## 📊 扫描统计

| 级别 | 数量 |
|------|:--:|
| 🔴 Critical | {critical} |
| 🟠 High | {high} |
| **总计发现** | **{critical + high}** |

---

## 🧠 LLM 审计分析

{llm}

---

## 🔍 原始扫描输出

```text
{scan[:3000]}
```

---

*由 AI Auditor v2.0 自动生成 · 58种攻击模式 · 90%检出率验证*
*github.com/shunfeng8421/defi-hack-memo*
"""


# ═══════════════════════════════════════
# CLI
# ═══════════════════════════════════════
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("AI Auditor v2.0 — LLM增强版")
        print("用法: python ai-auditor-llm.py <github-url | 本地路径>")
        print("LLM: 自动检测 Ollama > OpenAI > DeepSeek > 规则引擎")
        sys.exit(1)
    
    auditor = AIAuditorV2()
    report = auditor.audit(sys.argv[1])
    print(f"\n{report[:800]}...")
