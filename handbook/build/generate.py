#!/usr/bin/env python3
"""Generate PDF + HTML for DeFi Security Handbook"""
import markdown, os, re

HANDBOOK = r"D:\ll\knowledge-base\10-security\handbook"
OUTPUT = r"D:\ll\knowledge-base\10-security\handbook\build"

os.makedirs(OUTPUT, exist_ok=True)

# Chapter order
chapters = [
    ("README.md", True),  # Title + preface
    ("part1/ch01-why-defi-breaks.md", False),
    ("part1/ch02-toolkit.md", False),
    ("part1/ch03-reading-exploits.md", False),
    ("part2/ch04-flash-loans.md", False),
    ("part2/ch05-oracle-manipulation.md", False),
    ("part2/ch06-access-control.md", False),
    ("part2/ch07-token-economics.md", False),
    ("part2/ch08-cross-chain.md", False),
    ("part2/ch09-reentrancy.md", False),
    ("part2/ch10-initialization.md", False),
    ("part2/ch11-precision-gas.md", False),
    ("part2/ch12-governance.md", False),
    ("part3/ch13-solana.md", False),
    ("part4/ch14-mev-frontrunning.md", False),
    ("part4/ch15-lending-protocol-attacks.md", False),
    ("part4/ch16-dex-concentrated-liquidity.md", False),
    ("part4/ch17-depin-physical-layer.md", False),
    ("part4/ch18-zk-circuit.md", False),
    ("part4/ch19-rwa-tokenization.md", False),
    ("part4/ch20-gamefi-economics.md", False),
    ("part4/ch21-ai-agent-security.md", False),
    ("part5/ch22-security-scanner.md", False),
    ("part5/ch23-writing-effective-tests.md", False),
    ("part5/ch24-incident-response.md", False),
    ("appendix/A-complete-pattern-reference.md", False),
    ("appendix/B-real-world-loss-database.md", False),
    ("appendix/C-foundry-test-suite.md", False),
    ("appendix/D-scanner-configuration.md", False),
]

# Build full markdown
full_md = []
for path, is_readme in chapters:
    fp = os.path.join(HANDBOOK, path)
    if not os.path.exists(fp):
        print(f"  ⚠️ Missing: {path}")
        continue
    with open(fp, encoding='utf-8') as f:
        content = f.read()
    
    if is_readme:
        # Extract only preface + about sections (skip TOC for flow)
        parts = content.split('---')
        preface_start = content.find('## 序言')
        if preface_start > 0:
            content = content[preface_start:]
    else:
        # Remove "Next:" navigation links
        content = re.sub(r'\*Next:.*\*', '', content)
    
    full_md.append(content)
    full_md.append('\n\n---\n\\newpage\n\n')

combined = '\n\n'.join(full_md)

# Save combined markdown
combined_path = os.path.join(OUTPUT, "DeFi-Security-Handbook.md")
with open(combined_path, 'w', encoding='utf-8') as f:
    f.write(combined)
print(f"✅ Markdown: {len(combined):,} chars → {combined_path}")

# Generate HTML
html = markdown.markdown(combined, extensions=['fenced_code', 'tables', 'codehilite', 'toc'])
html_full = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>DeFi Security Handbook — Shiqiang Chen</title>
<style>
body {{ font-family: Georgia, serif; max-width: 800px; margin: 0 auto; padding: 2em; line-height: 1.8; color: #1a1a1a; }}
h1 {{ font-size: 2em; border-bottom: 3px solid #1a1a1a; padding-bottom: 0.3em; }}
h2 {{ font-size: 1.5em; margin-top: 2em; border-bottom: 1px solid #ccc; }}
code {{ background: #f5f5f5; padding: 0.2em 0.4em; font-size: 0.9em; }}
pre {{ background: #1a1a1a; color: #f8f8f2; padding: 1em; overflow-x: auto; border-radius: 4px; }}
pre code {{ background: none; padding: 0; }}
@media print {{ body {{ font-size: 11pt; }} }}
</style>
</head>
<body>
{html}
</body>
</html>"""

html_path = os.path.join(OUTPUT, "DeFi-Security-Handbook.html")
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_full)
print(f"✅ HTML: {len(html_full):,} chars → {html_path}")

# Try PDF with weasyprint
try:
    from weasyprint import HTML
    pdf_path = os.path.join(OUTPUT, "DeFi-Security-Handbook.pdf")
    HTML(filename=html_path).write_pdf(pdf_path)
    pdf_size = os.path.getsize(pdf_path)
    print(f"✅ PDF: {pdf_size:,} bytes → {pdf_path}")
except Exception as e:
    print(f"⚠️ PDF failed: {e}")
    print("   Install: pip install weasyprint")
    print(f"   Open HTML in browser → Print → Save as PDF")

print("\n📚 Generation complete!")
