# -*- coding: utf-8 -*-
"""Generate CN PDFs for papers 06, 07, 08."""
import subprocess, os, tempfile, markdown

PAPER_CSS = """
@page { size: A4; margin: 25mm 22mm 28mm 22mm;
    @bottom-center { content: counter(page); font-family: 'DengXian', 'Microsoft YaHei', sans-serif; font-size: 8pt; color: #808080; }
}
body { font-family: 'DengXian', 'Microsoft YaHei', 'SimSun', serif; font-size: 10pt; line-height: 1.65; color: #1a1a1a; text-align: justify; }
h1 { font-size: 16pt; font-weight: bold; color: #111; margin-top: 0; margin-bottom: 8pt; text-align: center; }
h2 { font-size: 13pt; font-weight: bold; color: #1e1e1e; margin-top: 18pt; margin-bottom: 6pt; page-break-after: avoid; }
h3 { font-size: 11pt; font-weight: bold; color: #323232; margin-top: 12pt; margin-bottom: 4pt; page-break-after: avoid; }
p { margin: 4pt 0; }
blockquote { margin: 8pt 0; padding: 6pt 12pt; border-left: 3pt solid #5a5a5a; background: #f8f8f8; font-size: 9pt; color: #444; page-break-inside: avoid; }
pre { background: #f5f5f5; border: 0.5pt solid #c8c8c8; padding: 8pt 10pt; font-family: 'Consolas', 'Courier New', monospace; font-size: 7.5pt; line-height: 1.35; color: #282828; white-space: pre-wrap; word-wrap: break-word; margin: 6pt 0; page-break-inside: avoid; }
code { font-family: 'Consolas', 'Courier New', monospace; font-size: 8.5pt; background: #f0f0f0; padding: 1pt 3pt; }
pre code { background: none; padding: 0; font-size: 7.5pt; }
table { border-collapse: collapse; margin: 8pt 0; width: 100%; font-size: 8.5pt; page-break-inside: avoid; }
th { background: #282828; color: white; padding: 5pt 6pt; font-weight: bold; }
td { border: 0.5pt solid #a0a0a0; padding: 4pt 6pt; }
"""

PAPERS = [
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\06-taxonomy\CN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper\06-taxonomy\CN.pdf",
        "title": "DeFi 攻击模式综合分类法",
    },
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\07-hardening-gradient\CN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper\07-hardening-gradient\CN.pdf",
        "title": "安全硬化梯度：DeFi 攻击防御时间分析",
    },
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\08-eip712-errors\CN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper\08-eip712-errors\CN.pdf",
        "title": "当类型哈希说谎：EIP-712 实现中的隐蔽签名验证错误",
    },
]

chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

for p in PAPERS:
    md_path = p["md"]
    pdf_path = p["pdf"]
    title = p["title"]
    
    print(f"\n[PDF] {os.path.basename(md_path)}")
    
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    md_html = markdown.markdown(md_content, extensions=['fenced_code', 'tables', 'codehilite', 'nl2br'])
    
    html_str = '<!DOCTYPE html>\n<html lang="zh">\n<head>\n<meta charset="utf-8">\n<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n%s\n</body>\n</html>' % (title, PAPER_CSS, md_html)
    
    # Save HTML alongside PDF
    html_path = pdf_path.replace('.pdf', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_str)
    
    output_abs = os.path.abspath(pdf_path)
    os.makedirs(os.path.dirname(output_abs), exist_ok=True)
    
    cmd = [chrome, '--headless', '--disable-gpu', '--no-sandbox',
           '--print-to-pdf=' + output_abs, '--no-pdf-header-footer',
           'file:///' + html_path.replace('\\', '/')]
    
    print("  Running Chrome headless...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    
    if os.path.exists(output_abs):
        size_kb = os.path.getsize(output_abs) / 1024
        print(f"  PDF: {os.path.basename(pdf_path)} ({size_kb:.1f} KB)")
    else:
        print(f"  FAILED: {result.stderr[:200] if result.stderr else 'no output'}")

print("\nAll done!")
