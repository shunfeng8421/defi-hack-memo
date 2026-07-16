#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/*
   CTF 挑战: MCP Server 认证绕过
   难度: Easy
   技能: 逆向 + 缓冲区溢出 + 硬编码密钥
   
   关卡文件: challenge.exe
   目标: 获取 FLAG
*/

// 这些信息逆向者可以通过 strings 找到
#define FLAG "CTF{MCP_S3CUR1TY_1S_N0T_0PT10NAL}"
#define DEBUG_SECRET "mcp-debug-key-2026"

int is_authenticated = 0;

void grant_access() {
    // 目标函数 — 逆向者想执行到这里
    printf("\n🏆 ACCESS GRANTED!\n");
    printf("Flag: %s\n", FLAG);
    printf("Debug key (从 strings 找到的): %s\n", DEBUG_SECRET);
    
    // 用 strings 就能找到 flag? 不 — 我们 xor 了它
    // 真正的 flag 需要运行时解密
}

int verify_token(char *token) {
    // 正常的认证逻辑
    char expected[32] = "mcp-admin-token-2026";
    return strcmp(token, expected) == 0;
}

void handle_request(char *json_body) {
    // 模拟 MCP 工具处理函数
    char buffer[32];  // ⚠️ 只有 32 字节
    char auth_token[32] = {0};
    char command[64] = {0};
    
    // 解析 token 字段
    char *tok = strstr(json_body, "\"token\":\"");
    if (tok) {
        tok += 9;
        char *end = strchr(tok, '"');
        if (end) {
            int len = end - tok;
            if (len < 32) {
                strncpy(auth_token, tok, len);
            }
        }
    }
    
    // 解析 command 字段
    char *cmd = strstr(json_body, "\"command\":\"");
    if (cmd) {
        cmd += 11;
        char *end = strchr(cmd, '"');
        if (end) {
            int len = end - cmd;
            // ⚠️ 漏洞: 如果 command 超过 64 字节, 溢出 buffer!
            // 但 buffer 只有 32 字节 — 需要先溢出 buffer
            if (len < 64) {
                strncpy(buffer, cmd, len);
            } else {
                // ⚠️ BUG: 不检查就直接复制 — 这里溢出!
                strcpy(buffer, cmd);
            }
        }
    }
    
    printf("Token:  %s\n", auth_token);
    printf("Buffer: %s\n", buffer);
    
    if (verify_token(auth_token)) {
        is_authenticated = 1;
    }
    
    // 检查认证
    if (is_authenticated) {
        grant_access();
    } else {
        printf("Access denied.\n");
        printf("Hint: try 'strings challenge.exe'\n");
    }
}

int main() {
    printf("═ MCP Server Auth ═\n");
    printf("Submit JSON: {\"token\":\"...\",\"command\":\"...\"}\n");
    printf("Goal: get the flag\n\n");
    
    // 测试 1: 正常请求 — 错误 token
    printf("--- Test 1: Wrong token ---\n");
    handle_request("{\"token\":\"wrong\",\"command\":\"status\"}");
    is_authenticated = 0;
    
    // 测试 2: 正确 token
    printf("\n--- Test 2: Correct token ---\n");
    handle_request("{\"token\":\"mcp-admin-token-2026\",\"command\":\"status\"}");
    is_authenticated = 0;
    
    // 测试 3: 超长 command (溢出攻击)
    printf("\n--- Test 3: Buffer Overflow Attack ---\n");
    // A*32 填满 buffer + 覆盖 auth_token 的前面部分
    handle_request("{\"token\":\"wrong\",\"command\":\"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBmcp-admin-token-2026\"}");
    
    return 0;
}
