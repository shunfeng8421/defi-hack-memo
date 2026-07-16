#!/usr/bin/env python3
"""
知识库 MCP 服务器 — shunfeng8421
=================================
把你的 34 模式/40 规则/25+ 文档变成 AI 可查询的服务

MCP 工具:
  search_knowledge  — 全文搜索整个知识库
  get_pattern       — 获取指定漏洞模式
  list_patterns     — 列出所有 34 个模式
  get_cwe_info      — 获取 CWE 详情
  list_semgrep_rules — 列出所有 Semgrep 规则
  get_report_template — 获取报告模板
"""

import os
import re
import json
import asyncio
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

KB = Path(r"D:\ll\knowledge-base\10-security")
GRAPH = KB / "knowledge-graph.json"

# ═══════════════════════════════════════════
# 核心函数
# ═══════════════════════════════════════════

def search_knowledge(query: str, max_results: int = 5) -> list:
    """全文搜索知识库"""
    results = []
    query_lower = query.lower()
    words = query_lower.split()
    
    for f in KB.rglob("*.md"):
        if f.name.startswith("."):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
            text_lower = text.lower()
            
            # 计算匹配分数
            score = sum(1 for w in words if w in text_lower)
            if score > 0:
                # 找最佳片段
                for w in words:
                    idx = text_lower.find(w)
                    if idx >= 0:
                        start = max(0, idx - 80)
                        end = min(len(text), idx + 120)
                        snippet = text[start:end].replace("\n", " ")
                        results.append({
                            "file": f.name,
                            "score": score / len(words),
                            "snippet": f"...{snippet}..."
                        })
                        break
        except:
            pass
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_results]


def get_pattern(pattern_id: str) -> dict:
    """获取指定漏洞模式"""
    patterns_file = KB / "01-patterns.md"
    if not patterns_file.exists():
        return {"error": "Patterns file not found"}
    
    text = patterns_file.read_text(encoding="utf-8", errors="replace")
    pattern_id = pattern_id.replace("#", "").strip()
    
    # 找模式块
    pattern = re.search(
        rf'###\s+{re.escape(pattern_id)}\.\s+(.+?)(?=###|$)',
        text, re.DOTALL
    )
    if pattern:
        return {
            "id": pattern_id,
            "title": pattern.group(1).strip()[:80],
            "content": pattern.group(0)[:500]
        }
    return {"error": f"Pattern #{pattern_id} not found"}


def list_all_patterns() -> list:
    """从所有文件提取模式列表"""
    patterns = []
    for f in KB.rglob("*.md"):
        if f.name.startswith("."):
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        matches = re.findall(r'###\s+([#W]?\d+\.?\s*.+?)$', text, re.MULTILINE)
        for m in matches:
            patterns.append({"file": f.name, "title": m.strip()[:60]})
    return patterns


def get_cwe_info(cwe_id: str) -> dict:
    """获取 CWE 详情"""
    cwe_file = KB / "03-cwe-top25.md"
    if not cwe_file.exists():
        return {"error": "CWE file not found"}
    
    text = cwe_file.read_text(encoding="utf-8", errors="replace")
    pattern = re.search(
        rf'CWE-{re.escape(cwe_id.replace("CWE-",""))}.*?(?=CWE-|$)',
        text, re.DOTALL
    )
    if pattern:
        return {"cwe": f"CWE-{cwe_id}", "content": pattern.group(0)[:400]}
    return {"error": f"CWE-{cwe_id} not found"}


def list_semgrep_rules() -> dict:
    """列出所有 Semgrep 规则"""
    rules = {}
    for f in KB.rglob("*.yaml"):
        if "rules" in f.name.lower() or "semgrep" in f.name.lower():
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
                count = text.count("- id:")
                rules[f.name] = count
            except:
                pass
    return rules


def get_report_template() -> str:
    """获取报告模板"""
    template_file = KB / "hackerone-template.md"
    if template_file.exists():
        return template_file.read_text(encoding="utf-8", errors="replace")[:1000]
    return "## Vulnerability Report Template\n..."


def query_graph(node_id: str) -> dict:
    """查询知识图谱 — 找到所有关联的节点"""
    if not GRAPH.exists():
        return {"error": "Knowledge graph not found"}
    
    data = json.loads(GRAPH.read_text())
    nodes = data.get("nodes", {})
    edges = data.get("edges", [])
    
    if node_id not in nodes:
        return {"error": f"Node '{node_id}' not found", "available": list(nodes.keys())[:10]}
    
    node = nodes[node_id]
    result = {"node": node, "connections": []}
    
    for conn_id in node.get("connects_to", []):
        if conn_id in nodes:
            # Find the edge relation
            relation = "related"
            for e in edges:
                if (e["from"] == node_id and e["to"] == conn_id) or \
                   (e["from"] == conn_id and e["to"] == node_id):
                    relation = e["relation"]
            result["connections"].append({
                "id": conn_id,
                "name": nodes[conn_id].get("name", conn_id),
                "type": nodes[conn_id].get("type", "?"),
                "relation": relation,
                "fix": nodes[conn_id].get("fix", "")
            })
    
    return result

# ═══════════════════════════════════════════
# MCP 服务器
# ═══════════════════════════════════════════

app = Server("shunfeng-knowledge-base")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_knowledge",
            description="全库搜索 34 模式/40 规则/CWE/exploit 相关内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索词"},
                    "max_results": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_pattern",
            description="获取指定漏洞模式的详细信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern_id": {"type": "string", "description": "模式ID, 如 15 或 1"}
                },
                "required": ["pattern_id"]
            }
        ),
        Tool(
            name="list_patterns",
            description="列出全部 34 个漏洞模式索引",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_cwe_info",
            description="获取 CWE 分类详情",
            inputSchema={
                "type": "object",
                "properties": {
                    "cwe_id": {"type": "string", "description": "CWE ID, 如 22 或 306"}
                },
                "required": ["cwe_id"]
            }
        ),
        Tool(
            name="list_semgrep_rules",
            description="列出所有 Semgrep 规则统计 (40条/7语言)",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_report_template",
            description="获取标准安全报告模板",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="query_graph",
            description="查询知识图谱 — 找出与指定节点(如 CWE-22, pattern-15)关联的所有节点",
            inputSchema={
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "节点ID: CWE-22, pattern-15, cherrystudio-cve-1 等"}
                },
                "required": ["node_id"]
            }
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "search_knowledge":
        results = search_knowledge(
            arguments["query"],
            arguments.get("max_results", 5)
        )
        return [TextContent(type="text", text=json.dumps(results, indent=2, ensure_ascii=False))]
    
    elif name == "get_pattern":
        result = get_pattern(arguments["pattern_id"])
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    
    elif name == "list_patterns":
        patterns = list_all_patterns()
        return [TextContent(type="text", text=json.dumps(patterns, indent=2, ensure_ascii=False))]
    
    elif name == "get_cwe_info":
        result = get_cwe_info(arguments["cwe_id"])
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    
    elif name == "list_semgrep_rules":
        rules = list_semgrep_rules()
        return [TextContent(type="text", text=json.dumps(rules, indent=2, ensure_ascii=False))]
    
    elif name == "get_report_template":
        template = get_report_template()
        return [TextContent(type="text", text=template)]
    
    elif name == "query_graph":
        result = query_graph(arguments["node_id"])
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    
    return [TextContent(type="text", text="Unknown tool")]

async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
