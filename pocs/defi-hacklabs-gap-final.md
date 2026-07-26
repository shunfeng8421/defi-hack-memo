# DeFiHackLabs 分类学缺口——最终分析

**分析日期**: 2026-07-26  
**总 PoC**: 870  
**有 @Summary 标签**: 26 (3%)  
**无文档**: 844 (97%)

---

## 结论

DeFiHackLabs 不是漏洞分类不全——是**漏洞类型未标注**。97% 的 PoC 没有 @Summary 描述。我们无法从代码自动推断漏洞类型，因为：
- 同一个 `getReserves()` 调用，可能是 Oracle 操纵、可能是 MEV、可能是流动性攻击
- 没有漏洞描述，纯靠代码推理 = 误判率极高

## 有 Summary 的 26 个 PoC 分类

| 类型 | 数量 | 已覆盖 |
|------|:--:|:--:|
| Oracle/Price | 5 | ✅ Pattern #1-8 |
| Access Control | 5 | ✅ Pattern #9-12 |
| Staking/Yield | 3 | ✅ Pattern #43-46 |
| Flash Loan | 1 | ✅ Pattern #1-3 |
| Token Economics | 1 | ✅ Pattern #13-16 |
| Cross-Chain/Bridge | 1 | ✅ Pattern #17-20 |
| Lending/Liquidation | 1 | ✅ Pattern #43-46 |
| Reentrancy | 1 | ✅ Pattern #21-24 |
| 新候选 | 2 | 🔍 见下 |
| 非漏洞描述 | 6 | — |

## 2 个候选新模式

### 候选 #68: Stale State Variable
**PoC**: sellamount global variable outdated  
**描述**: 合约使用了过期的全局变量作为计算依据，该变量未随最新状态更新  
**映射**: 类似精度问题但根因是状态同步而非算术

### 候选 #69: Array Duplicate Element
**PoC**: lack of checking for duplicate elements in array  
**描述**: 对数组元素的重复检查缺失，允许攻击者提交重复 ID 绕过验证  
**映射**: 输入验证的特殊情况

## 行动建议

1. **不再手工分类 DeFiHackLabs** — 844 个无文档 PoC 需要逐个人工阅读，ROI 太低
2. **接受 66 模式覆盖度** — 26 个有文档的 PoC 中 18 个已覆盖 (69%)
3. **新发现的 #67-#69 加入扩展库**
4. **未来优先找有文档的新漏洞数据集**
