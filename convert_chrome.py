# -*- coding: utf-8 -*-
"""Convert Markdown papers to PDF using Chrome headless -- perfect CJK rendering."""
import markdown
import subprocess
import os, sys, tempfile, time

# ============================================================
# CSS - Academic paper style for Chrome print
# ============================================================
PAPER_CSS = """
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
@page :first {
    @top-center {
        content: none;
    }
}

body {
    font-family: 'DengXian', 'Microsoft YaHei', 'SimSun', serif;
    font-size: 10pt;
    line-height: 1.65;
    color: #1a1a1a;
    text-align: justify;
}

h1 {
    font-size: 16pt;
    font-weight: bold;
    color: #111;
    margin-top: 0;
    margin-bottom: 8pt;
    text-align: center;
}

h2 {
    font-size: 13pt;
    font-weight: bold;
    color: #1e1e1e;
    margin-top: 18pt;
    margin-bottom: 6pt;
    page-break-after: avoid;
}

h3 {
    font-size: 11pt;
    font-weight: bold;
    color: #323232;
    margin-top: 12pt;
    margin-bottom: 4pt;
    page-break-after: avoid;
}

p {
    margin: 4pt 0;
}

blockquote {
    margin: 8pt 0;
    padding: 6pt 12pt;
    border-left: 3pt solid #5a5a5a;
    background: #f8f8f8;
    font-size: 9pt;
    color: #444;
    page-break-inside: avoid;
}
blockquote p {
    margin: 2pt 0;
}

hr {
    border: none;
    border-top: 1pt solid #ccc;
    margin: 14pt 0;
}

pre {
    background: #f5f5f5;
    border: 0.5pt solid #c8c8c8;
    padding: 8pt 10pt;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 7.5pt;
    line-height: 1.35;
    color: #282828;
    white-space: pre-wrap;
    word-wrap: break-word;
    overflow-wrap: break-word;
    margin: 6pt 0;
    page-break-inside: avoid;
}

code {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8.5pt;
    background: #f0f0f0;
    padding: 1pt 3pt;
}
pre code {
    background: none;
    padding: 0;
    font-size: 7.5pt;
}

table {
    border-collapse: collapse;
    margin: 8pt 0;
    width: 100%;
    font-size: 8.5pt;
    page-break-inside: avoid;
}
th {
    background: #282828;
    color: white;
    padding: 4pt 6pt;
    text-align: left;
    font-weight: bold;
}
td {
    padding: 3pt 6pt;
    border: 0.5pt solid #ccc;
}
tr:nth-child(even) td {
    background: #fafafa;
}

ul, ol {
    margin: 4pt 0;
    padding-left: 22pt;
}
li {
    margin: 2pt 0;
}

strong {
    color: #111;
}

a {
    color: #2a5db0;
    text-decoration: none;
}

/* Don't break headings from their content */
h2, h3 {
    page-break-after: avoid;
}
h2 + p, h3 + p, h2 + ul, h3 + ul, h2 + ol, h3 + ol,
h2 + pre, h3 + pre, h2 + table, h3 + table {
    page-break-before: avoid;
}
"""

def build_html(md_path: str, title: str) -> str:
    """Convert Markdown to styled HTML."""
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    md_html = markdown.markdown(
        md_content,
        extensions=['fenced_code', 'tables', 'codehilite', 'nl2br']
    )
    
    # Inject paper title into the first h1's string-set for page headers
    css = PAPER_CSS
    
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>%s</title>
<style>%s</style>
</head>
<body>
%s
</body>
</html>""" % (title, css, md_html)


def chrome_print_html(html_str: str, output_pdf: str):
    """Print HTML to PDF using Chrome headless."""
    with tempfile.NamedTemporaryFile(suffix='.html', mode='w', 
                                      encoding='utf-8', delete=False) as f:
        f.write(html_str)
        html_path = f.name
    
    # Also save a copy alongside the PDF for debugging
    debug_html = output_pdf.replace('.pdf', '.html')
    with open(debug_html, 'w', encoding='utf-8') as f:
        f.write(html_str)
    
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome):
        chrome = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    
    output_abs = os.path.abspath(output_pdf)
    os.makedirs(os.path.dirname(output_abs), exist_ok=True)
    
    cmd = [
        chrome,
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        '--print-to-pdf=' + output_abs,
        '--no-pdf-header-footer',
        'file:///' + html_path.replace('\\', '/'),
    ]
    
    print("  Running Chrome headless...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    # Clean up temp file
    try:
        os.unlink(html_path)
    except:
        pass
    
    if result.returncode != 0:
        print("  stderr:", result.stderr[:500])
        raise RuntimeError("Chrome exited with code %d" % result.returncode)
    
    # Wait for file to be written
    time.sleep(1)
    
    if not os.path.exists(output_pdf):
        raise RuntimeError("PDF not created: %s" % output_pdf)
    
    size_kb = os.path.getsize(output_pdf) / 1024
    print("  PDF: %s (%.1f KB)" % (os.path.basename(output_pdf), size_kb))


def generate(md_path: str, output_pdf: str, title: str):
    print("\n[PDF] %s" % os.path.basename(md_path))
    html_str = build_html(md_path, title)
    chrome_print_html(html_str, output_pdf)


PAPERS = [
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\01-prompt-injection\EN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper-prompt-injection-v2.pdf",
        "title": "Prompt Injection is Not an AI Problem",
    },
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\02-mcp-taxonomy\EN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper-mcp-taxonomy-v2.pdf",
        "title": "An Empirical Study of MCP Server Security",
    },
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\03-defi-evolution\EN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper-deFi-v2.pdf",
        "title": "The Evolution of DeFi Security",
    },
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\04-decade-analysis\EN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper\04-decade-analysis\EN.pdf",
        "title": "A Decade of DeFi Attacks 2017-2026",
    },
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\04-decade-analysis\CN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper\04-decade-analysis\CN.pdf",
        "title": "DeFi Attack Decade Analysis",
    },
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\05-flash-loan-evolution\EN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper\05-flash-loan-evolution\EN.pdf",
        "title": "Flash Loan Attacks: A Decade of Evolution",
    },
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\05-flash-loan-evolution\CN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper\05-flash-loan-evolution\CN.pdf",
        "title": "Flash Loan Attacks: Decade Evolution (CN)",
    },
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\06-taxonomy\EN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper\06-taxonomy\EN.pdf",
        "title": "Comprehensive Taxonomy of DeFi Attack Patterns",
    },
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\07-hardening-gradient\EN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper\07-hardening-gradient\EN.pdf",
        "title": "The Hardening Gradient",
    },
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\08-eip712-errors\EN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper\08-eip712-errors\EN.pdf",
        "title": "When Type Hashes Lie: EIP-712 Errors",
    },
]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        idx = int(sys.argv[1]) - 1
        p = PAPERS[idx]
        generate(p["md"], p["pdf"], p["title"])
    else:
        for i, p in enumerate(PAPERS):
            print("\n[%d/%d]" % (i+1, len(PAPERS)))
            generate(p["md"], p["pdf"], p["title"])
    
    print("\nAll done!")
