#!/usr/bin/env python3
"""
Coverage-Guided Fuzzer — Level 2
=================================
从 Level 1 (盲猜) 升级到 Level 2 (用覆盖信息指导变异)

核心原理:
  1. 随机生成输入
  2. 运行目标函数 → 记录哪些代码行被执行了
  3. 如果输入触达了"新代码" → 保留为种子
  4. 基于种子继续变异 → 产生更深层的输入
  5. 循环 → 直到崩溃或找到目标

类比:
  Level 1 = 蒙眼扔飞镖
  Level 2 = 每次扔完看一眼靶子在哪儿，调整方向再扔
"""

import sys
import random
import string
import traceback

# ═══════════════════════════════════════════
# 目标: 一个含有隐藏 bug 的函数
# ═══════════════════════════════════════════

def target_function(path: str) -> str:
    """
    模拟 MCP 工具的文件路径处理函数
    包含多个隐藏的 bug 触发条件
    """
    result = []
    
    # Bug 1: 路径穿越检测不完整
    if ".." in path:
        result.append("PATH_TRAVERSAL_ATTEMPT")
    
    # Bug 2: 空字节截断后读了不该读的文件
    if "\x00" in path:
        # 只检查了 split 后的第一部分
        safe_part = path.split("\x00")[0]
        if not safe_part.startswith("/safe/"):
            result.append("NULL_BYTE_BYPASS")
    
    # Bug 3: URL 编码的路径穿越绕过了检查
    if "%2e%2e" in path.lower() or "%2f" in path.lower():
        result.append("ENCODED_TRAVERSAL")
    
    # Bug 4: Unicode 规范化后变成 ../ 
    import unicodedata
    normalized = unicodedata.normalize("NFKC", path)
    if ".." in normalized and ".." not in path:
        result.append("UNICODE_BYPASS")
    
    # Bug 5: Windows 绝对路径绕过了 Unix 检查
    if path.startswith("C:\\") or path.startswith("\\\\"):
        result.append("WINDOWS_PATH_BYPASS")
    
    # Bug 6: 符号链接 /proc/self/root 绕过
    if "/proc/" in path and "/root" in path:
        result.append("PROC_SYMLINK_BYPASS")
    
    # Bug 7: 嵌套深度 > 10 的 ../ 导致缓冲区溢出(模拟)
    depth = path.count("../") + path.count("..\\")
    if depth > 10:
        result.append("DEEP_TRAVERSAL_CRASH")
        # ⚠️ 真正的 bug: 如果 depth > 20, 触发崩溃
        if depth > 20:
            raise RuntimeError(f"BUFFER OVERFLOW at depth {depth}!")
    
    # Bug 8: 特定组合触发隐藏的认证绕过
    if "admin" in path.lower() and "\x00" in path and ".." in normalized:
        result.append("AUTH_BYPASS_CHAIN")
    
    return " | ".join(result) if result else "OK"


# ═══════════════════════════════════════════
# 覆盖追踪器
# ═══════════════════════════════════════════

import sys
import types

class CoverageTracker:
    """追踪 target_function 内部哪些行被执行了"""
    
    def __init__(self):
        self.seen_lines = set()  # 已经见过的代码行
        self.total_bugs_found = 0
        self.crashes = 0
    
    def trace_callback(self, frame, event, arg):
        """sys.settrace 回调 — 每执行一行代码就调用"""
        if event == "line":
            line_no = frame.f_lineno
            self.seen_lines.add(line_no)
        return self.trace_callback
    
    def start(self):
        sys.settrace(self.trace_callback)
    
    def stop(self):
        sys.settrace(None)
    
    def reset(self):
        self.seen_lines = set()


# ═══════════════════════════════════════════
# 变异引擎
# ═══════════════════════════════════════════

class Mutator:
    """从种子生成变体 — 类似 AFL 的变异策略"""
    
    def __init__(self):
        self.operators = [
            self._flip_byte,        # 翻转一个字节
            self._insert_string,    # 插入已知危险字符串
            self._delete_chunk,     # 删除一段
            self._duplicate_chunk,  # 复制一段
            self._replace_percent,  # URL 编码变换
            self._unicode_expand,   # Unicode 扩展
            self._repeat_pattern,   # 重复某个模式
        ]
    
    def mutate(self, seed: str) -> str:
        """对种子随机应用 1-3 个变异算子"""
        s = seed
        for _ in range(random.randint(1, 3)):
            op = random.choice(self.operators)
            s = op(s)
        return s
    
    def _flip_byte(self, s: str) -> str:
        if not s: return s
        pos = random.randint(0, len(s) - 1)
        return s[:pos] + chr(random.randint(0, 255)) + s[pos+1:]
    
    def _insert_string(self, s: str) -> str:
        dangers = ["../", "..\\", "\x00", "%2e%2e", "%2f", "C:\\", "/proc/self/root"]
        pos = random.randint(0, len(s))
        return s[:pos] + random.choice(dangers) + s[pos:]
    
    def _delete_chunk(self, s: str) -> str:
        if len(s) < 3: return s
        start = random.randint(0, len(s) - 2)
        end = random.randint(start + 1, len(s))
        return s[:start] + s[end:]
    
    def _duplicate_chunk(self, s: str) -> str:
        if len(s) < 2: return s
        start = random.randint(0, len(s) - 2)
        end = random.randint(start + 1, min(start + 10, len(s)))
        return s[:end] + s[start:end] + s[end:]
    
    def _replace_percent(self, s: str) -> str:
        return s.replace("/", "%2f").replace(".", "%2e")
    
    def _unicode_expand(self, s: str) -> str:
        replacements = {"/": "\u2215", ".": "\u2024", "\\": "\u2216"}
        for old, new in replacements.items():
            if random.random() < 0.3:
                s = s.replace(old, new)
        return s
    
    def _repeat_pattern(self, s: str) -> str:
        return s + "../" * random.randint(1, 15)


# ═══════════════════════════════════════════
# 覆盖引导 Fuzzer
# ═══════════════════════════════════════════

class CoverageGuidedFuzzer:
    def __init__(self, target_func, max_iterations=1000):
        self.target = target_func
        self.max_iterations = max_iterations
        self.tracker = CoverageTracker()
        self.mutator = Mutator()
        
        # 种子池: 只有触达新代码的输入才保留
        self.seeds = ["/safe/data.txt", "test", "", "admin"]
        self.all_bugs = set()
        self.crashes = []
    
    def run(self):
        print(f"Coverage-Guided Fuzzer")
        print(f"Target: {self.target.__name__}")
        print(f"Seeds: {len(self.seeds)}")
        print(f"Max iterations: {self.max_iterations}")
        print("-" * 50)
        
        for i in range(self.max_iterations):
            self._step(i)
            
            if i % 200 == 0 and i > 0:
                print(f"  ...{i} iterations, {len(self.seeds)} seeds, "
                      f"{len(self.all_bugs)} bugs, {len(self.crashes)} crashes")
        
        self._report()
    
    def _step(self, iteration):
        # 1. 从种子池选一个种子
        seed = random.choice(self.seeds)
        
        # 2. 变异
        test_input = self.mutator.mutate(seed)
        
        # 3. 重置覆盖
        self.tracker.reset()
        
        # 4. 运行目标函数
        old_coverage = len(self.tracker.seen_lines)
        self.tracker.start()
        try:
            result = self.target(test_input)
            self.tracker.stop()
        except Exception as e:
            self.tracker.stop()
            self.crashes.append((test_input, str(e)))
            return
        
        # 5. 检查覆盖增长
        new_coverage = len(self.tracker.seen_lines)
        
        # 6. 如果触达了新代码 → 保留为种子!
        if new_coverage > old_coverage:
            self.seeds.append(test_input)
        
        # 7. 记录 bug
        if result != "OK":
            for bug in result.split(" | "):
                if bug not in self.all_bugs:
                    self.all_bugs.add(bug)
                    print(f"  🐛 [{iteration}] {bug}: {test_input[:60]}")
    
    def _report(self):
        print("\n" + "=" * 50)
        print("FUZZING COMPLETE")
        print("=" * 50)
        print(f"Total iterations: {self.max_iterations}")
        print(f"Final seed pool:  {len(self.seeds)}")
        print(f"Unique bugs found: {len(self.all_bugs)}")
        print(f"Crashes:           {len(self.crashes)}")
        print(f"Code lines covered: {len(self.tracker.seen_lines)}")
        print()
        print("Bugs discovered:")
        for bug in sorted(self.all_bugs):
            print(f"  ✅ {bug}")
        if self.crashes:
            print(f"\n💥 Crashes:")
            for inp, err in self.crashes[:3]:
                print(f"  {err}: {inp[:60]}")


if __name__ == "__main__":
    fuzzer = CoverageGuidedFuzzer(target_function, max_iterations=500)
    fuzzer.run()
