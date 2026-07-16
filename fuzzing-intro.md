# Fuzzing 入门 — 基于已验证的漏洞

## 三个层次

### Level 1: 基于模板的 Fuzzing（今天能学会）
用已知漏洞模式生成输入变体

```
已知: file_path → open() 无验证
Fuzz: 生成 1000 个路径变体
  ../../etc/passwd
  ....//....//etc/passwd
  /%2e%2e/%2e%2e/etc/passwd
  /..%252f..%252fetc/passwd
  \..\..\windows\win.ini
  自动测试哪个能绕过过滤
```

**用 cherrystudio 做教材**：写一个 fuzzer 对 `file_path` 参数生成 1000 个路径变体。

---

### Level 2: 覆盖率引导的 Fuzzing（1-2周学会）
用代码覆盖率知道"输入触达了哪些代码"

```
工具: pythonfuzz / libFuzzer / AFL
原理: 
  1. 随机生成输入
  2. 运行程序
  3. 记录覆盖率（哪些代码被执行了）
  4. 只有"触达新代码"的输入才保留
  5. 以此为种子继续变异
  6. 循环直到崩溃
```

---

### Level 3: 协议 Fuzzing（1-2月学会）
Fuzz 网络协议本身

```
不是 Fuzz 路径 → 而是 Fuzz MCP JSON-RPC 消息
  生成: {"method":"tools/call", "params":{"name": "X"*10000}}
  生成: {"method":"\x00\x00\x00"}
  生成: {"jsonrpc":"2.0","id":-1,"method":"tools/call"}
  → 哪个能让服务器崩溃？
```

---

## 今天做 Level 1

写 cherrystudio 路径遍历 Fuzzer：
- 输入: 目标文件路径
- 输出: 1000 个绕过变体
- 验证: 哪个变体成功读取了目标文件
