#!/usr/bin/env python3
"""
二进制逆向入门 — 用 Python 理解底层原理
=========================================
逆向的本质: 从字节码/汇编 → 还原程序逻辑

今天学三个核心概念:
  1. 编译 = 源码 → 字节码 (Python dis 模块)
  2. 反汇编 = 字节码 → 可读指令
  3. 控制流 = 指令跳转 → if/for/while

类比:
  C 程序 → GCC → x86机器码 → objdump → 汇编 → 逆向工程师读懂
  Python → compile → bytecode → dis → 字节码 → 我们读懂
"""

import dis   # Python 的反汇编器
import struct # 二进制数据打包

# ═══════════════════════════════════════════
# 第一课: 看你的代码变成了什么
# ═══════════════════════════════════════════

def simple_login(password: str) -> bool:
    """一个简单的登录函数 — 逆向者想理解这个逻辑"""
    if password == "admin123":
        return True
    return False

print("=" * 55)
print("第一课: 源码 → 字节码")
print("=" * 55)
print("\n源码:")
import inspect
print(inspect.getsource(simple_login))
print("\n反汇编结果 (类似 x86 的 objdump 输出):")
dis.dis(simple_login)


# ═══════════════════════════════════════════
# 第二课: 控制流 — if/loop 在底层长什么样
# ═══════════════════════════════════════════

def check_access(role: str, level: int) -> str:
    """访问控制 — 逆向者想找到绕过方法"""
    if role == "admin":
        return "ALLOWED"          # ← 逆向者要找的是这个 return
    elif level >= 5:
        return "ELEVATED"
    else:
        return "DENIED"

print("\n" + "=" * 55)
print("第二课: 控制流还原")
print("=" * 55)
print("\n源码:")
print(inspect.getsource(check_access))
print("\n反汇编 — 注意 JUMP 指令:")
dis.dis(check_access)
print("\n解读:")
print("  LOAD_FAST 'role'  → 加载参数")
print("  LOAD_CONST 'admin' → 加载比较值")
print("  COMPARE_OP ==      → 比较")
print("  POP_JUMP_IF_FALSE  → 不相等就跳到下一个检查 (这就是 if!)")
print("  LOAD_CONST 'ALLOWED' → 相等就返回 ALLOWED")
print("  RETURN_VALUE       → 函数结束")


# ═══════════════════════════════════════════
# 第三课: 反向工程 — 给定字节码，猜源码
# ═══════════════════════════════════════════

def mystery_function(x):
    """
    ❓ 你不知道这个函数的源码
    但你可以反汇编它，从字节码逆向出逻辑
    这就是逆向工程师每天做的事
    """
    return x * 2 + 1 if x > 10 else x * 3

print("\n" + "=" * 55)
print("第三课: 逆向工程 — 从字节码还原逻辑")
print("=" * 55)
print("\n你看到的只有这个:")
dis.dis(mystery_function)
print()
print("还原过程:")
print("  LOAD_FAST x → LOAD_CONST 10 → COMPARE_OP >")
print("  → 如果 x > 10: LOAD_FAST x → LOAD_CONST 2 → BINARY_MULTIPLY → LOAD_CONST 1 → BINARY_ADD")
print("  → 否则: LOAD_FAST x → LOAD_CONST 3 → BINARY_MULTIPLY")
print()
print("还原结果: return x * 2 + 1 if x > 10 else x * 3")


# ═══════════════════════════════════════════
# 第四课: 二进制格式 — 内存中的布局
# ═══════════════════════════════════════════

print("\n" + "=" * 55)
print("第四课: 二进制数据 — struct 模块")
print("=" * 55)

# 和 C 语言的 struct 完全一样
# 逆向者需要知道这些二进制布局

# 模拟一个网络协议包
packet = struct.pack("!I4s", 0xDEADBEEF, b"PING")
print(f"原始字节: {packet.hex()}")

# 逆向: 从字节还原
length, command = struct.unpack("!I4s", packet)
print(f"还原: length=0x{length:08X}, command={command}")

# ELF/PE 文件头也是这个原理
print("\n类比:")
print("  ELF 文件头 = struct.pack('16sHHIIIIIHHHHHH', ...)")
print("  PE 文件头  = struct.pack('4sHHIIIIHH', ...)")
print("  → 逆向工具(Ghidra/IDA)也是用 struct 解析的!")


# ═══════════════════════════════════════════
# 第五课: 实战 — 绕过登录检查
# ═══════════════════════════════════════════

PASSWORD = "s3cr3t!"

def check_password(user_input: str) -> bool:
    """逆向者想绕过这个检查"""
    if user_input == PASSWORD:
        return True
    return False

print("\n" + "=" * 55)
print("第五课: 实战 — 绕过密码检查")
print("=" * 55)
print()
dis.dis(check_password)
print()
print("逆向者的思路:")
print("  看到 COMPARE_OP == → 需要用户输入等于 PASSWORD")
print("  看到 LOAD_CONST 's3cr3t!' → 这就是密码!")
print("  结论: 不需要绕过 — 直接从字节码里读出了密码")
print()
print("在真实二进制中:")
print("  strings ./program | grep s3cr3t  → 同样能找到硬编码密码")
