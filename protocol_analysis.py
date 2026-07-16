#!/usr/bin/env python3
"""
网络协议分析 — 从 TCP 到 MCP JSON-RPC
========================================
协议栈: TCP → HTTP → JSON-RPC → MCP
每一层都是一层封装

今天学三个核心概念:
  1. 协议分层 — 数据怎么一层层包的
  2. 抓包分析 — 看懂字节流里的秘密
  3. MCP 协议 — JSON-RPC 的完整请求/响应
"""

import socket
import struct
import json

# ═══════════════════════════════════════════
# 第一课: 协议分层 — 洋葱模型
# ═══════════════════════════════════════════

print("=" * 55)
print("第一课: 协议分层 — 数据怎么包的")
print("=" * 55)
print()
print("MCP 协议栈 (从外到内):")
print("  ┌─────────────────────────────┐")
print("  │  TCP (端口号、序列号、校验和)   │ ← 传输层: 可靠传输")
print("  │  ├─────────────────────────┤")
print("  │  │  HTTP (方法、路径、头)      │ │ ← 应用层: Web 通信")
print("  │  │  ├─────────────────────┤  │")
print("  │  │  │  JSON-RPC (方法、参数) │  │ │ ← RPC 层: 远程调用")
print("  │  │  │  ├─────────────────┤   │ │")
print("  │  │  │  │  MCP Tool Args   │   │ │ │ ← 业务层: 工具参数")
print("  │  │  │  └─────────────────┘   │ │")
print("  └──┴──┴─────────────────────────┴──┘")

# ═══════════════════════════════════════════
# 第二课: 构造一个完整的 MCP 请求包
# ═══════════════════════════════════════════

print()
print("=" * 55)
print("第二课: 构造 MCP 请求 — 看每一层加了什么")
print("=" * 55)
print()

# MCP 业务数据
tool_args = {"file_path": "/etc/passwd", "content": ""}

# JSON-RPC 层
jsonrpc_payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "qq_upload_file",
        "arguments": tool_args
    }
}
jsonrpc_body = json.dumps(jsonrpc_payload).encode()
print(f"JSON-RPC body: {len(jsonrpc_body)} bytes")
print(f"  {jsonrpc_body[:80]}...")
print()

# HTTP 层
http_request = (
    f"POST /mcp HTTP/1.1\r\n"
    f"Host: localhost:8080\r\n"
    f"Content-Type: application/json\r\n"
    f"Content-Length: {len(jsonrpc_body)}\r\n"
    f"Mcp-Session-Id: abc123def456\r\n"
    f"\r\n"
).encode() + jsonrpc_body
print(f"HTTP + JSON-RPC: {len(http_request)} bytes (+{len(http_request) - len(jsonrpc_body)} HTTP headers)")
print(f"  {http_request[:100]}...")
print()

# TCP 层 (简化 — 真实中还要算 TCP 头 20 字节 + IP 头 20 字节)
tcp_overhead = 40
total_on_wire = len(http_request) + tcp_overhead
print(f"TCP + IP overhead: {tcp_overhead} bytes")
print(f"Total on wire: {total_on_wire} bytes")
print()
print("每层比例:")
print(f"  MCP args:      {len(json.dumps(tool_args))} bytes")
print(f"  + JSON-RPC:    +{len(jsonrpc_body) - len(json.dumps(tool_args))} bytes")
print(f"  + HTTP:        +{len(http_request) - len(jsonrpc_body)} bytes")
print(f"  + TCP/IP:      +{tcp_overhead} bytes")
print(f"  = 总字节:      {total_on_wire} bytes")

# ═══════════════════════════════════════════
# 第三课: 协议分析实战 — 从字节流还原请求
# ═══════════════════════════════════════════

print()
print("=" * 55)
print("第三课: 逆向分析 — 给定原始字节流，还原请求")
print("=" * 55)
print()

# 模拟抓包截获的原始字节流 (类似 Wireshark 显示)
raw_bytes = http_request
print("原始字节流 (hex):")
print(raw_bytes[:80].hex())
print()

# 步骤 1: 找 HTTP 头结束 (第一个 \r\n\r\n)
headers_end = raw_bytes.find(b"\r\n\r\n")
headers = raw_bytes[:headers_end].decode()
body = raw_bytes[headers_end + 4:]

print("还原 HTTP 头:")
for line in headers.split("\r\n"):
    if line.startswith("POST") or line.startswith("Content") or "Session" in line:
        print(f"  {line}")

# 步骤 2: 解析 JSON-RPC body
rpc = json.loads(body)
print(f"\n还原 JSON-RPC:")
print(f"  method: {rpc['method']}")
print(f"  tool:   {rpc['params']['name']}")

# 步骤 3: 提取工具参数 — 这就是攻击面
args = rpc['params']['arguments']
print(f"\n⚠️ MCP 工具参数 (攻击面):")
print(f"  {args}")

# ═══════════════════════════════════════════
# 第四课: 网络层 — TCP 三次握手 + 数据传输
# ═══════════════════════════════════════════

print()
print("=" * 55)
print("第四课: TCP 层 — 三次握手")
print("=" * 55)
print()

print("""
Wireshark 抓到的 MCP 连接:
  CLIENT → SYN              → SERVER  (1. 我要连接)
  CLIENT ← SYN+ACK          ← SERVER  (2. 好,请继续)
  CLIENT → ACK              → SERVER  (3. 收到)
  CLIENT → POST /mcp HTTP/1.1 →       (4. 发请求)
  CLIENT ← HTTP/1.1 200 OK  ← SERVER  (5. 响应)
  CLIENT → FIN              → SERVER  (6. 关闭)

用 tcpdump 看:
  tcpdump -A -i lo port 8080
  可以看到完整的 HTTP + JSON-RPC 内容
""")

# ═══════════════════════════════════════════
# 第五课: MCP 协议安全分析
# ═══════════════════════════════════════════

print()
print("=" * 55)
print("第五课: MCP 协议安全分析")
print("=" * 55)
print()

print("""
从协议角度分析 MCP 安全:

1. 传输层 (TCP/HTTP)
   ─ 数据是否加密?  HTTP vs HTTPS
   ─ 是否可被中间人篡改?  无 TLS = 可篡改

2. 会话层 (Mcp-Session-Id)
   ─ Session ID 是否可预测?
   ─ 是否可劫持其他用户的会话?

3. RPC 层 (JSON-RPC)
   ─ method 参数是否白名单?
   ─ 是否允许调用未公开的方法?

4. 工具层 (Tool Args)
   ─ file_path 是否有路径验证?  ← cherrystudio CVE
   ─ URL 参数是否过滤?          ← SSRF
   ─ SQL 参数是否参数化?        ← SQL 注入

Wireshark 过滤器:
  http.host contains "mcp"        → 只看 MCP 流量
  jsonrpc.method == "tools/call"  → 只看工具调用
  tcp.port == 8080                → 只看特定端口
""")
