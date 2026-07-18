# 工作总梳理 — 2026年7月

## 一、DeFi 安全（核心主线）

### 数据基础
- 824 DeFiHackLabs 案例全部提取、分类、索引
- 870个PoC文件全库扫描: 9,827个发现
- 10个已知攻击验证: 90%检出率 ($1.07B覆盖)

### 50模式分类学
- 50种攻击模式完整分类（业界最全，Werner 2023仅12种）
- 97.6%覆盖率
- 50条扫描规则 + 50个Slither检测器

### 漏洞猎杀（9个确认，$23.22M）
Whalebit、Aztec、DxSale、VerusBridge、futureswap、CurveLlamaLend、AlkemiEarn、BCE Token、Smart Account

### 区块链深耕模块
跨链桥 · MEV sandwich · ZK证明 · EVM底层 · 闪贷8大PoC

---

## 二、AI Agent × DeFi（新领域开创）

- 8个全新攻击向量（全球首次系统分类）
- 5个项目审计: Clicks/Cairn/AgentPM/PropFund/YerbaMate
- 13个发现，覆盖7/8向量
- 全球首个AI Agent × DeFi安全扫描器（8向量检测）
- Foundry沙盒验证代码

---

## 三、论文（9篇）
01-08: Prompt Injection/MCP/DeFi演化/十年分析/闪贷/50模式分类/硬化梯度/EIP-712
09: AI Agent × DeFi Security（最新）

---

## 四、工具链
- 主扫描器: DeFi 50 + AI Agent 8 = 58模式
- GitHub Action 自动扫描器
- 7个Foundry PoC项目
- 50道Solidity习题（含exploit+fix）
- 知识图谱: 99→171节点

---

## 五、网站
shunfeng8421.github.io/defi-hack-memo/
├── 年度报告 2026
├── 攻击手册（50模式可搜索）
└── AI Agent × DeFi 研究

---

## 六、赏金 & 披露
- BattleChain 4个发现（评审中）
- Olympus 负责任披露
- Tare $50K 备战（7/20开赛）

## 七、投稿
- 竹南生《都挺好的》→ ONE/单读/天涯/上海文学

## 八、基础设施
- 飞书通道修复 + 开机自启
- GitHub仓库清理（102→8核心）
- Email实名认证
- 自动看门狗

---

**核心资产**: 9论文 · 58检测规则 · 9漏洞 · 7 PoC · 50习题 · 824案例 · 171图谱
