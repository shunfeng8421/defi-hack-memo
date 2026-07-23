# Zenodo Upload Guide — EIP-712 Taxonomy Paper

## 📋 上传信息速览

| 项目 | 内容 |
|------|------|
| **上传地址** | https://zenodo.org/deposit/new |
| **格式** | PDF（主文件）+ MD / DOCX / HTML（补充材料） |
| **许可** | **CC BY 4.0**（推荐允许最广的传播和引用） |

---

## 1️⃣ 元数据（Metadata）

### Title（标题）
```
When Type Hashes Lie: A Systematic Study of EIP-712 Implementation Errors in DeFi Protocols
```

> 中文版可选副标题（在 Description 中补充）

### Authors（作者）
```
Chen, Shiqiang
```
- **Affiliation**: Independent Researcher
- **ORCID**: （如有则填写，无则留空）
- **Email**: shunfeng8421@163.com

### Description（摘要 / 描述）

**英文（直接复制到 Description 框）：**

```
EIP-712 (Typed Structured Data Hashing and Signing) has become ubiquitous in DeFi, enabling gasless transactions, permit-based approvals, and cross-chain message signing. However, the specification's complexity—requiring precise coordination between Solidity contract code and off-chain signing libraries—creates subtle failure modes that evade conventional smart contract auditing.

This paper presents the first systematic taxonomy of EIP-712 implementation errors, derived from the analysis of 824 DeFi vulnerability reports and validated through 4 confirmed exploits totaling over $3.7M in losses.

We identify six error categories:
- Category I: Struct-Field Mismatch (CRITICAL) - TYPEHASH includes a bytes field but inner struct fields are not individually listed
- Category II: Missing Replay Protection (HIGH) - nonce, chainId, or deadline omitted from signed message
- Category III: Typographical Errors (MEDIUM) - misspelled type names (addres, byts, etc.) causing fund locks
- Category IV: Type Confusion (HIGH) - type mismatches between Solidity struct and TYPEHASH (address vs uint256, bytes vs bytes32)
- Category V: Domain Separator Inconsistencies (HIGH) - missing chainId, field ordering errors
- Category VI: Inheritance/Upgrade Layout Incompatibility (MEDIUM) - struct changes without TYPEHASH regeneration

For each category, we provide real-world exploitation evidence, canonical attack scenarios, formal definitions, detection heuristics, and automated scanning rules. We evaluate our scanner against 47 confirmed EIP-712 incidents, achieving 90% detection rate with 7.0% false positive rate.

We release an open-source EIP-712 vulnerability scanner (Patterns #27-#32) as part of the 58-pattern DeFi security toolkit.

This work is accompanied by:
- Chinese language version (CN.pdf / CN.docx)
- Source markdown (EN.md / CN.md)
- Professional Word documents (EN.docx / CN.docx)
- Web-ready HTML (EN.html / CN.html)

Keywords: EIP-712, typed signatures, DeFi security, vulnerability taxonomy, smart contract auditing, TYPEHASH, Ethereum, cross-chain replay
```

### Keywords（关键词）

直接粘贴这些：
```
EIP-712, typed signatures, DeFi security, vulnerability taxonomy, smart contract auditing, TYPEHASH, Ethereum, cross-chain replay, blockchain security, signature verification
```

### License（许可协议）
选择 **Creative Commons Attribution 4.0 International (CC BY 4.0)**

### Access Type
选择 **Open Access**

### DOI
选择 **"Reserve DOI"**（Zenodo 会自动生成。如果已有上传过相关的项目，可以选"所属项目"关联）

### Upload Date
选择 **今天**（July 23, 2026）

### Communities
搜索并勾选以下社区：
- `zenodo`（默认）
- 可选：`Ethereum Research`、`Blockchain Security`

### Grants
留空（本工作无资助项目）

---

## 2️⃣ 文件清单（Files）

### 推荐上传结构

| 文件 | 类型 | 说明 | 必传 |
|------|------|------|:----:|
| `EN.pdf` | PDF | **主论文 - 英文版** | ✅ 必要 |
| `CN.pdf` | PDF | 中文版全文（可选但推荐） | ⭐ 推荐 |
| `EN.md` | Markdown | 源码版本，便于他人编辑/复现 | ⭐ 推荐 |
| `CN.md` | Markdown | 中文源码版本 | 可选 |
| `EN.docx` | Word | 可编辑文档格式 | ⭐ 推荐 |
| `CN.docx` | Word | 中文可编辑文档 | 可选 |
| `EN.html` | HTML | 浏览器友好版本 | 可选 |
| `CN.html` | HTML | 中文浏览器友好版本 | 可选 |

> 最少上传 `EN.pdf` + `EN.md` + `EN.docx` 即可。
> 如果想展示中英文双语，再加上 `CN.pdf`。

### 上传 Drag-and-Drop
直接从文件夹把文件拖进 Zenodo 上传区域即可。顺序无所谓，Zenodo 会按文件名排序显示。

---

## 3️⃣ 操作步骤（Step-by-Step）

```
1. 打开 https://zenodo.org/ → 点击 "Sign in"（用 GitHub 或 ORCID 登录）
2. 点击右上角头像 → "Deposit" → "New Upload"
3. 拖拽文件到上传区域（推荐 EN.pdf + EN.md + EN.docx）
4. 填写元数据：
   a. Title: 粘贴上面的英文标题
   b. Authors: 输入名字，可以搜索 ORCID
   c. Description: 粘贴上面写好的描述
   d. Keywords: 粘贴关键词列表
   e. License: 选 CC BY 4.0
   f. Access: Open Access
   g. DOI: 点击 "Reserve DOI"
5. 填写完成后点 "Save" 保存草稿
6. 检查预览效果
7. 点击 "Publish" 正式发布
```

---

## 4️⃣ 发布后引用格式

发布后 Zenodo 会生成 DOI。引用格式（APA）：

```
Chen, S. (2026). When Type Hashes Lie: A Systematic Study of EIP-712 Implementation Errors in DeFi Protocols. Zenodo. https://doi.org/xxxxx
```

BibTeX 格式（可直接复制到论文中引用自己）：

```bibtex
@techreport{chen2026eip712,
  author      = {Chen, Shiqiang},
  title       = {When Type Hashes Lie: A Systematic Study of EIP-712 Implementation Errors in DeFi Protocols},
  year        = {2026},
  month       = jul,
  institution = {Zenodo},
  doi         = {10.5281/zenodo.XXXXX},
  url         = {https://doi.org/10.5281/zenodo.XXXXX}
}
```

---

## 5️⃣ 可与之前论文关联

如果之前在 Zenodo 发布过 **"When AI Agents Start Trading"**（AI Agent × DeFi 论文），可以在 "Related/Alternate Identifiers" 中关联它：

| 类型 | 标识符 |
|------|--------|
| **被伴随** | 填写上一篇论文的 DOI（如已发布） |
| **相关资源** | `https://github.com/shunfeng8421/defi-hack-memo` |

---

*以上所有内容可以直接复制到 Zenodo 表单中。如果需要我帮你调整任何部分，直接说！*
