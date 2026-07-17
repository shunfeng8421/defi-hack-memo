# -*- coding: utf-8 -*-
"""LaTeX to HTML conversion for 04-decade-analysis paper, then PDF via Chrome."""
import subprocess, os, time, tempfile

# ============================================================
# CSS
# ============================================================
CSS = """
@page {
    size: A4;
    margin: 25mm 22mm 28mm 22mm;
    @bottom-center {
        content: counter(page);
        font-family: 'DengXian', 'Microsoft YaHei', sans-serif;
        font-size: 8pt;
        color: #808080;
    }
}

body {
    font-family: 'DengXian', 'Microsoft YaHei', 'SimSun', serif;
    font-size: 10pt;
    line-height: 1.6;
    color: #1a1a1a;
    text-align: justify;
}

h1 {
    font-size: 15pt;
    font-weight: bold;
    color: #111;
    text-align: center;
    margin-top: 0;
    margin-bottom: 4pt;
}

.author {
    text-align: center;
    font-size: 9pt;
    color: #555;
    margin-bottom: 2pt;
}
.date {
    text-align: center;
    font-size: 9pt;
    color: #555;
    margin-bottom: 16pt;
}

h2 {
    font-size: 12pt;
    font-weight: bold;
    color: #1e1e1e;
    margin-top: 16pt;
    margin-bottom: 4pt;
    page-break-after: avoid;
}

h3 {
    font-size: 10.5pt;
    font-weight: bold;
    color: #323232;
    margin-top: 10pt;
    margin-bottom: 3pt;
    page-break-after: avoid;
}

p {
    margin: 3pt 0;
}

.abstract {
    font-style: italic;
    margin: 8pt 0 14pt 0;
    padding: 6pt 10pt;
    background: #f8f8f8;
    border-left: 2pt solid #888;
    font-size: 9.5pt;
}

ul {
    margin: 4pt 0;
    padding-left: 20pt;
}
li {
    margin: 2pt 0;
}

table {
    border-collapse: collapse;
    margin: 8pt auto;
    font-size: 8.5pt;
    page-break-inside: avoid;
}
th {
    background: #282828;
    color: white;
    padding: 3pt 6pt;
    text-align: left;
}
td {
    padding: 2pt 6pt;
    border: 0.5pt solid #ccc;
}
.caption {
    text-align: center;
    font-size: 8.5pt;
    font-weight: bold;
    margin: 6pt 0 2pt 0;
}

.formula {
    text-align: center;
    margin: 8pt 0;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
}
"""

# ============================================================
# English HTML
# ============================================================
EN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>A Decade of DeFi Attacks: Pattern Evolution 2017-2026</title>
<style>""" + CSS + """</style>
</head>
<body>

<h1>A Decade of DeFi Attacks: Pattern Evolution 2017–2026</h1>
<p class="author">Shiqiang Chen</p>
<p class="date">July 2026 &nbsp;|&nbsp; github.com/shunfeng8421/defi-hack-memo</p>

<div class="abstract">
We analyze 824 confirmed DeFi security incidents (2017–2026), the largest empirical study of its kind. Attacks shifted from high-value flash loan exploits ($600M+ peaks) to small-scale permission bugs (median $50K in 2025). 17 unique patterns are identified; flash loan + oracle manipulation dominates (24% cases, 60% losses). DeFi risk index (loss/TVL) declined 30% from 2020 to 2025. 2026 introduces novel precision + backdoor + accounting attacks. Large protocols harden; small projects remain vulnerable.
</div>

<h2>1. Introduction</h2>
<p>DeFi has lost over $10B to security incidents. Systematic empirical analysis of pattern evolution across the full DeFi era has been lacking. We catalog all 824 attacks from DeFiHackLabs, covering Parity (2017) to Aztec (June 2026).</p>

<h2>2. Data &amp; Classification</h2>

<h3>2.1 Sources</h3>
<ul>
<li>DeFiHackLabs (SunWeb3Sec): 824 PoC contracts</li>
<li>Rekt News, security firms (CertiK, SlowMist): loss verification</li>
</ul>

<h3>2.2 17-Pattern Taxonomy</h3>
<p class="caption">Table 1: Attack Pattern Classification</p>
<table>
<tr><th>ID</th><th>Pattern</th><th>Example</th></tr>
<tr><td>#1</td><td>Flash Loan + Oracle</td><td>bZx $50M, Cream $130M</td></tr>
<tr><td>#2</td><td>Reentrancy</td><td>LendfMe $25M, JoeAgent $45K</td></tr>
<tr><td>#5</td><td>ERC-4626 Inflation</td><td>vault-core</td></tr>
<tr><td>#6</td><td>Lending Liquidation</td><td>Euler $197M, Radiant $4.5M</td></tr>
<tr><td>#7</td><td>AMM Manipulation</td><td>Gamma $6.3M, Velocore $6.88M</td></tr>
<tr><td>#8</td><td>Governance Attack</td><td>Beanstalk $182M</td></tr>
<tr><td>#13</td><td>Admin Key/Privilege</td><td>Ronin $600M, Bybit $1.5B</td></tr>
<tr><td>#27</td><td>Signature Replay</td><td>Poly $610M, Nomad $152M</td></tr>
<tr><td>#34</td><td>Cross-Chain</td><td>Wormhole $320M</td></tr>
<tr><td>#46</td><td>Precision Loss</td><td>BEC $1.5B</td></tr>
</table>

<h2>3. Results</h2>

<h3>3.1 Temporal Evolution</h3>
<p class="caption">Table 2: Attack Evolution by Year</p>
<table>
<tr><th>Year</th><th>Dominant Pattern</th><th>Peak Loss</th><th>Median Loss</th></tr>
<tr><td>2017–18</td><td>Contract bugs</td><td>$170M</td><td>$20M</td></tr>
<tr><td>2020</td><td>Flash loan emergence</td><td>$50M</td><td>$15M</td></tr>
<tr><td>2021</td><td>Flash loan + oracle peak</td><td>$610M</td><td>$5M</td></tr>
<tr><td>2022</td><td>Cross-chain bridge era</td><td>$600M</td><td>$3M</td></tr>
<tr><td>2023</td><td>Lending/liquidation</td><td>$197M</td><td>$500K</td></tr>
<tr><td>2024</td><td>Multi-vector combos</td><td>$48M</td><td>$200K</td></tr>
<tr><td>2025</td><td>Permission bugs</td><td>$104M</td><td>$50K</td></tr>
<tr><td>2026</td><td>Precision + backdoor</td><td>$1.5B</td><td>$100K</td></tr>
</table>

<h3>3.2 Risk Index</h3>
<p class="formula">Risk = Total Annual Loss / Total Value Locked</p>
<p>Risk declined from 3.33% (2020) to 2.33% (2025), a 30% reduction. TVL growth outpaced loss growth despite more attacks.</p>

<h3>3.3 Flash Loan Dominance</h3>
<p>Flash loans enabled 24% of attacks but caused 60% of total losses ($6B+). TWAP and Chainlink adoption reduced new incidents by 40% post-2023.</p>

<h2>4. Discussion</h2>

<h3>4.1 The Hardening Gradient</h3>
<p>Protocols &gt;$1B TVL show few new vulnerabilities post-2024. Protocols &lt;$1M TVL still fall to basic bugs (access control, unchecked returns). Automated tools eliminated code-level bugs; design-level bugs now dominate.</p>

<h3>4.2 2026: A New Attack Class</h3>
<p>Precision errors + intentional backdoors + accounting inconsistencies characterize 2026. These resist automated detection—they require business logic understanding.</p>

<h2>5. Conclusion</h2>
<p>DeFi security measurably improved: risk index −30%. But the attack surface fragments: large protocols harden, small protocols remain exposed. The next frontier is detecting backdoors and complex accounting manipulations.</p>

<p style="margin-top:14pt;"><strong>Dataset:</strong> 10.5281/zenodo.21382653<br>
<strong>Repository:</strong> github.com/shunfeng8421/defi-hack-memo</p>

</body>
</html>"""

# ============================================================
# Chinese HTML
# ============================================================
CN_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>DeFi 攻击十年：2017-2026 模式演化</title>
<style>""" + CSS + """</style>
</head>
<body>

<h1>DeFi 攻击十年：2017–2026 模式演化</h1>
<p class="author">陈世强</p>
<p class="date">2026年7月 &nbsp;|&nbsp; github.com/shunfeng8421/defi-hack-memo</p>

<div class="abstract">
本文分析 824 个已确认的 DeFi 安全事件（2017–2026），是同类研究最大规模的实证研究。攻击模式从高额闪电贷利用（峰值超 $600M）演化为小规模权限 bug（2025年中位数 $50K）。识别出 17 种独特攻击模式。DeFi 风险指数从 3.33% 降至 2.33%。2026 年出现了精度错误+后门+会计不一致的新型攻击类别。
</div>

<h2>1. 引言</h2>
<p>DeFi 累计损失超 $100 亿。缺乏贯穿整个 DeFi 时代的系统实证分析。本文编目了从 Parity（2017）到 Aztec（2026年6月）的 824 次攻击。</p>

<h2>2. 数据与分类</h2>
<p>数据来源：DeFiHackLabs（824 个 PoC 合约）、Rekt News、安全公司报告。建立了 17 模式分类体系：闪电贷+预言机（#1，24%）、重入（#2）、借贷清算（#6）、AMM 操纵（#7）、治理攻击（#8）、管理员密钥（#13）、签名重放（#27）、跨链（#34）、精度损失（#46）等。</p>

<h2>3. 时间演化</h2>
<p>2017–2018：合约 bug（Parity $170M）。2020：闪电贷兴起（bZx $50M）。2021：高峰（Poly $610M）。2022：跨链桥时代（Ronin $600M）。2023：借贷激增（Euler $197M）。2024：多向量组合。2025：权限 bug 主导。2026：精度+后门+会计（Bybit $1.5B）。</p>

<h2>4. 风险指数与闪电贷</h2>
<p class="formula">Risk = Total Annual Loss / Total Value Locked</p>
<p>风险指数 3.33% → 2.33%，下降 30%。闪电贷促成 24% 攻击但造成 60% 损失（$6B+）。TWAP 和 Chainlink 采用使新事件减少 40%。</p>

<h2>5. 结论</h2>
<p>DeFi 安全可衡量改善。攻击面分裂——大协议硬化，小项目仍暴露。下一个前沿：检测后门和复杂会计操纵。</p>

<p style="margin-top:14pt;"><strong>数据集：</strong> 10.5281/zenodo.21382653</p>

</body>
</html>"""

# ============================================================
# Generate PDFs
# ============================================================
def html_to_pdf(html_str, output_pdf):
    with tempfile.NamedTemporaryFile(suffix='.html', mode='w',
                                      encoding='utf-8', delete=False) as f:
        f.write(html_str)
        html_path = f.name

    output_abs = os.path.abspath(output_pdf)
    os.makedirs(os.path.dirname(output_abs), exist_ok=True)

    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome):
        chrome = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    cmd = [
        chrome, '--headless', '--disable-gpu', '--no-sandbox',
        '--print-to-pdf=' + output_abs,
        '--no-pdf-header-footer',
        'file:///' + html_path.replace('\\', '/'),
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    try:
        os.unlink(html_path)
    except:
        pass

    if result.returncode != 0:
        raise RuntimeError("Chrome failed: " + result.stderr[:300])
    
    time.sleep(0.5)
    size_kb = os.path.getsize(output_pdf) / 1024
    print(f"  {os.path.basename(output_pdf)}: {size_kb:.1f} KB")

if __name__ == "__main__":
    base = r"D:\ll\knowledge-base\10-security\paper\04-decade-analysis"
    
    print("[EN] A Decade of DeFi Attacks")
    html_to_pdf(EN_HTML, os.path.join(base, "EN.pdf"))
    
    print("[CN] DeFi 攻击十年")
    html_to_pdf(CN_HTML, os.path.join(base, "CN.pdf"))
    
    print("Done!")
