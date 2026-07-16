#include <stdio.h>
#include <string.h>

// ═══════════════════════════════════════════
// 内存漏洞利用 — 三课合一
// ═══════════════════════════════════════════

// 第一课: 栈布局
void lesson1_stack_layout() {
    printf("═════ 第一课: 栈布局 ═════\n");
    int a = 0x41;
    char buf[16] = "HELLO";
    int b = 0x42;
    
    printf("a    addr: %p, value: 0x%x\n", &a, a);
    printf("buf  addr: %p, value: %s\n", buf, buf);
    printf("b    addr: %p, value: 0x%x\n", &b, b);
    printf("a 和 b 在 buf 两侧 — 溢出 buf 就能改 a 或 b\n\n");
}

// 第二课: 缓冲区溢出 — 覆盖相邻变量
void lesson2_overflow() {
    printf("═════ 第二课: 溢出覆盖相邻变量 ═════\n");
    int admin = 0;       // 0=普通用户
    char password[8];    // ⚠️ 只有 8 字节!
    
    printf("admin before: %d\n", admin);
    
    // 正常输入 — 6字节, 不溢出
    strncpy(password, "abc123", 7);
    printf("'abc123' -> admin=%d (正常)\n", admin);
    
    // ⚠️ 攻击: 输入 20 字节 — 溢出 password, 覆盖 admin!
    strncpy(password, "AAAABBBBCCCCDDDDEEEE", 20);
    printf("'AAAABBBBCCCCDDDDEEEE' -> admin=%d (被覆盖!)\n", admin);
    printf("→ 攻击者不需要知道密码 — 直接覆盖 admin 变量\n\n");
}

// 第三课: 看懂 CVE 报告里的漏洞描述
void lesson3_reading_cve() {
    printf("═════ 第三课: 看懂 CVE 报告 ═════\n");
    
    // 模拟 UltraVNC CVE-2026-7829
    char dest[16];  // 16字节的目标缓冲区
    
    printf("模拟 CVE-2026-7829 (UltraVNC off-by-one):\n");
    printf("  dest[16] — 只有 16 字节\n");
    
    // 正常: 15 字节 + NUL = 16, 刚好
    memset(dest, 0, 16);
    strncpy(dest, "123456789012345", 15);
    printf("  15字节输入: 安全 ✓\n");
    
    // ⚠️ 漏洞: 16 字节 + NUL = 17, 溢出 1 字节!
    memset(dest, 0, 16);
    strncpy(dest, "1234567890123456", 16);
    printf("  16字节输入: NUL 写到 dest[16] — 越界 1 字节! ⚠️\n");
    printf("  → 这就是 CVE-2026-7829 的原理\n");
    printf("  → 'off-by-one' = 边界检查差了一个字节\n\n");
}

int main() {
    lesson1_stack_layout();
    lesson2_overflow();
    lesson3_reading_cve();
    
    printf("═════ 核心收获 ═════\n");
    printf("1. 栈 = 连续的地址空间 — 溢出 buffer 就能改相邻变量\n");
    printf("2. 覆盖 admin 变量 = 权限提升 (Privilege Escalation)\n");
    printf("3. 覆盖返回地址 = 代码执行 (Code Execution / RCE)\n");
    printf("4. CVE 描述里的 'heap buffer overflow' = 堆上的 version\n");
    
    return 0;
}
