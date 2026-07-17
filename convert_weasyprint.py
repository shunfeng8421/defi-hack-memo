"""Convert Markdown papers to PDF using WeasyPrint with proper CJK font support."""
import markdown
from weasyprint import HTML, CSS
import sys, os

# ============================================================
# CSS - Academic paper style
# ============================================================
PAPER_CSS = """
@page {
    size: A4;
    margin: 25mm 22mm 28mm 22mm;
    @top-center {
        content: string(heading);
        font-family: 'DengXian', 'Microsoft YaHei', sans-serif;
        font-size: 7pt;
        color: #808080;
    }
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
    string-set: heading "";
}

h1 {
    font-size: 16pt;
    font-weight: bold;
    color: #111;
    margin-top: 0;
    margin-bottom: 8pt;
    text-align: center;
    string-set: heading "Prompt Injection is Not an AI Problem — Shiqiang Chen";
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

/* DOI block and metadata */
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

/* horizontal rule */
hr {
    border: none;
    border-top: 1pt solid #ccc;
    margin: 14pt 0;
}

/* Code blocks */
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

/* Tables */
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

/* Lists */
ul, ol {
    margin: 4pt 0;
    padding-left: 22pt;
}
li {
    margin: 2pt 0;
}

/* Strong */
strong {
    color: #111;
}

/* Links */
a {
    color: #2a5db0;
    text-decoration: none;
}

/* Abstract specifically */
h2#abstract + p {
    font-style: italic;
}
"""

def md_to_html(md_path: str, title: str) -> str:
    """Convert Markdown to a full HTML document with CSS."""
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    # Convert markdown to HTML body
    md_html = markdown.markdown(
        md_content,
        extensions=[
            'fenced_code',
            'tables', 
            'codehilite',
            'nl2br',
        ]
    )
    
    # Wrap in a full HTML document with CSS
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>{PAPER_CSS}</style>
</head>
<body>
{md_html}
</body>
</html>"""
    return full_html


def generate_pdf(md_path: str, output_pdf: str, title: str):
    """Generate PDF from Markdown using WeasyPrint."""
    print(f"Converting: {os.path.basename(md_path)} → {os.path.basename(output_pdf)}")
    
    html_str = md_to_html(md_path, title)
    
    # Save intermediate HTML for debugging
    html_path = output_pdf.replace('.pdf', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_str)
    print(f"  HTML saved: {html_path}")
    
    # Generate PDF
    HTML(string=html_str).write_pdf(output_pdf)
    
    size_kb = os.path.getsize(output_pdf) / 1024
    print(f"  PDF generated: {output_pdf} ({size_kb:.1f} KB)")


# ============================================================
# Paper configurations
# ============================================================
PAPERS = [
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\01-prompt-injection\EN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper-prompt-injection-v2-weasy.pdf",
        "title": "Prompt Injection is Not an AI Problem — Shiqiang Chen",
    },
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\02-mcp-taxonomy\EN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper-mcp-taxonomy-v2-weasy.pdf",
        "title": "An Empirical Study of MCP Server Security — Shiqiang Chen",
    },
    {
        "md": r"D:\ll\knowledge-base\10-security\paper\03-defi-evolution\EN.md",
        "pdf": r"D:\ll\knowledge-base\10-security\paper-deFi-v2-weasy.pdf",
        "title": "The Evolution of DeFi Security — Shiqiang Chen",
    },
]

if __name__ == "__main__":
    # Generate specific paper or all
    if len(sys.argv) > 1:
        idx = int(sys.argv[1]) - 1
        paper = PAPERS[idx]
        generate_pdf(paper["md"], paper["pdf"], paper["title"])
    else:
        for i, paper in enumerate(PAPERS):
            print(f"\n[{i+1}/{len(PAPERS)}]")
            generate_pdf(paper["md"], paper["pdf"], paper["title"])
    
    print("\n✅ All done!")
