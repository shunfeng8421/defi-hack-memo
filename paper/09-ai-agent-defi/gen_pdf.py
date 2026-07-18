# -*- coding: utf-8 -*-
"""Generate PDF for Paper 09."""
import subprocess, os, markdown

PAPER_CSS = """
@page { size: A4; margin: 25mm 22mm 28mm 22mm;
    @bottom-center { content: counter(page); font-family: 'Georgia', serif; font-size: 8pt; color: #808080; }
}
body { font-family: 'Georgia', 'Times New Roman', serif; font-size: 10pt; line-height: 1.65; color: #1a1a1a; text-align: justify; }
h1 { font-size: 16pt; font-weight: bold; color: #111; margin-top: 0; margin-bottom: 8pt; text-align: center; }
h2 { font-size: 13pt; font-weight: bold; color: #1e1e1e; margin-top: 18pt; margin-bottom: 6pt; page-break-after: avoid; }
h3 { font-size: 11pt; font-weight: bold; color: #323232; margin-top: 12pt; margin-bottom: 4pt; page-break-after: avoid; }
p { margin: 4pt 0; }
blockquote { margin: 8pt 0; padding: 6pt 12pt; border-left: 3pt solid #5a5a5a; background: #f8f8f8; font-size: 9pt; color: #444; page-break-inside: avoid; }
pre { background: #f5f5f5; border: 0.5pt solid #c8c8c8; padding: 8pt 10pt; font-family: 'Consolas', 'Courier New', monospace; font-size: 7.5pt; line-height: 1.35; color: #282828; white-space: pre-wrap; word-wrap: break-word; margin: 6pt 0; page-break-inside: avoid; }
code { font-family: 'Consolas', 'Courier New', monospace; font-size: 8.5pt; background: #f0f0f0; padding: 1pt 3pt; }
pre code { background: none; padding: 0; font-size: 7.5pt; }
table { border-collapse: collapse; margin: 8pt 0; width: 100%; font-size: 8pt; page-break-inside: avoid; }
th { background: #282828; color: white; padding: 5pt 6pt; font-weight: bold; }
td { border: 0.5pt solid #a0a0a0; padding: 4pt 6pt; }
"""

md_path = r"D:\ll\knowledge-base\10-security\paper\09-ai-agent-defi\EN.md"
pdf_path = r"D:\ll\knowledge-base\10-security\paper\09-ai-agent-defi\EN.pdf"
title = "When Agents Trade: A Comprehensive Taxonomy of the AI Agent x DeFi Attack Surface"
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

with open(md_path, "r", encoding="utf-8") as f:
    md_content = f.read()

md_html = markdown.markdown(md_content, extensions=['fenced_code', 'tables', 'codehilite', 'nl2br'])

html_str = '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n%s\n</body>\n</html>' % (title, PAPER_CSS, md_html)

html_path = pdf_path.replace('.pdf', '.html')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_str)

cmd = [chrome, '--headless', '--disable-gpu', '--no-sandbox',
       '--print-to-pdf=' + os.path.abspath(pdf_path), '--no-pdf-header-footer',
       'file:///' + html_path.replace('\\', '/')]

print("[PDF] EN.md -> Running Chrome headless...")
result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)

if os.path.exists(pdf_path):
    size_kb = os.path.getsize(pdf_path) / 1024
    lines = md_content.count('\n')
    words = len(md_content.split())
    print("PDF: EN.pdf (%.1f KB) | %d lines | ~%d words" % (size_kb, lines, words))
else:
    print("FAILED:", result.stderr[:200] if result.stderr else 'no output')
