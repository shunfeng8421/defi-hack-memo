#!/usr/bin/env python3
"""Convert expanded MCP Taxonomy paper to PDF for Zenodo v2.0.0."""
from fpdf import FPDF
import re

INPUT_MD = r"D:\ll\knowledge-base\10-security\paper\02-mcp-taxonomy\EN.md"
OUTPUT_PDF = r"D:\ll\knowledge-base\10-security\paper-mcp-taxonomy-v2.pdf"

with open(INPUT_MD, "r", encoding="utf-8") as f:
    content = f.read()

class PaperPDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(True, 22)
        self.add_font("ZH", "", r"C:\Windows\Fonts\msyh.ttc")
        self.add_font("ZH", "B", r"C:\Windows\Fonts\msyhbd.ttc")
        self.add_font("MS", "", r"C:\Windows\Fonts\consola.ttf")
        self.add_font("MS", "B", r"C:\Windows\Fonts\consolab.ttf")
        self.add_page()
        self.pw = self.w - self.l_margin - self.r_margin
        self.normal_font = "ZH"
        self.code_font = "MS"
        self.code_size = 7.5

    def header(self):
        if self.page_no() > 1:
            self.set_font(self.normal_font, "", 7)
            self.set_text_color(128,128,128)
            self.cell(0, 4, "An Empirical Study of MCP Server Security — Shiqiang Chen", align="C")
            self.ln(6)

    def footer(self):
        self.set_y(-18)
        self.set_font(self.normal_font, "", 7)
        self.set_text_color(128,128,128)
        self.cell(0, 8, str(self.page_no()), align="C")

    def h2(self, text):
        self.ln(4)
        self.set_font(self.normal_font, "B", 13)
        self.set_text_color(30,30,30)
        self.multi_cell(self.pw, 7, text, align="L")
        self.ln(1)

    def h3(self, text):
        self.ln(2)
        self.set_font(self.normal_font, "B", 11)
        self.set_text_color(50,50,50)
        self.multi_cell(self.pw, 6, text, align="L")
        self.set_x(self.l_margin)

    def para(self, text):
        self.set_font(self.normal_font, "", 10)
        self.set_text_color(20,20,20)
        text = text.strip()
        if text:
            self.multi_cell(self.pw, 5.2, text, align="L")
            self.set_x(self.l_margin)

    def bullet(self, text):
        self.set_font(self.normal_font, "", 10)
        self.set_text_color(20,20,20)
        self.cell(5, 5.2, "-")
        self.multi_cell(self.pw - 5, 5.2, text.strip(), align="L")
        self.set_x(self.l_margin)

    def numbered(self, num, text):
        self.set_font(self.normal_font, "", 10)
        self.set_text_color(20,20,20)
        self.cell(8, 5.2, f"{num}.")
        self.multi_cell(self.pw - 8, 5.2, text.strip(), align="L")
        self.set_x(self.l_margin)

    def code_block(self, code):
        self.ln(2)
        self.set_fill_color(245,245,245)
        self.set_draw_color(200,200,200)
        self.set_font(self.code_font, "", self.code_size)
        self.set_text_color(40,40,40)
        max_chars = int(self.pw / self.get_string_width("x")) - 2  # -2: space prefix + safety
        for line in code.split('\n'):
            line = line.replace('\t', '    ')
            # Truncate until line fits (monospace code may lack word breaks)
            while self.get_string_width(" " + line) > self.pw and len(line) > 0:
                line = line[:-1]
            self.multi_cell(self.pw, 3.8, " " + line, fill=True)
            self.set_x(self.l_margin)
        self.ln(3)

    def mini_table(self, headers, rows, col_widths):
        self.ln(2)
        self.set_font(self.normal_font, "B", 8)
        self.set_fill_color(40,40,40)
        self.set_text_color(255,255,255)
        h = 6
        for i, hdr in enumerate(headers):
            x = self.get_x()
            self.multi_cell(col_widths[i], h, " " + hdr, fill=True, border=1)
            self.set_xy(x + col_widths[i], self.get_y() - h)
        self.ln(h + 1)
        self.set_font(self.normal_font, "", 8)
        self.set_text_color(20,20,20)
        alt = False
        for row in rows:
            if alt:
                self.set_fill_color(245,245,245)
            else:
                self.set_fill_color(255,255,255)
            alt = not alt
            max_lines = 1
            cell_texts = []
            for i, cell_val in enumerate(row):
                text = " " + str(cell_val)
                n = self.multi_cell(col_widths[i], 5.5, text, dry_run=True, output="LINES")
                lines = len(n) if n else 1
                max_lines = max(max_lines, lines)
                cell_texts.append(text)
            row_h = max_lines * 5.5
            y_start = self.get_y()
            for i, text in enumerate(cell_texts):
                x = self.get_x()
                self.multi_cell(col_widths[i], 5.5, text, fill=True, border=1)
                self.set_xy(x + col_widths[i], y_start)
            self.set_y(y_start + row_h)
        self.ln(3)

    def title_page(self):
        self.ln(20)
        self.set_font(self.normal_font, "B", 15)
        self.set_text_color(0,0,0)
        self.multi_cell(self.pw, 8, "An Empirical Study of Model Context Protocol (MCP)\nServer Security: Taxonomy, Large-Scale Scanning,\nand Defense Framework", align="C")
        self.ln(5)
        self.set_font(self.normal_font, "", 12)
        self.set_text_color(60,60,60)
        self.cell(self.pw, 8, "Shiqiang Chen", align="C")
        self.ln(8)
        self.set_font(self.normal_font, "", 9)
        self.set_text_color(120,120,120)
        self.cell(self.pw, 6, "Independent Researcher", align="C")
        self.ln(6)
        self.cell(self.pw, 6, "shunfeng8421@163.com  |  July 2026  |  cs.CR", align="C")
        self.ln(10)
        # Abstract
        self.set_font(self.normal_font, "B", 10)
        self.set_text_color(0,0,0)
        self.cell(0, 6, "Abstract")
        self.ln(8)
        self.set_font(self.normal_font, "", 9)
        self.set_text_color(40,40,40)
        abstract = ("The Model Context Protocol (MCP) has rapidly emerged as the dominant standard for AI agent tool "
                    "integration, with over 620 MCP server packages published across npm and PyPI ecosystems as of July 2026. "
                    "However, the security implications of a protocol that grants LLM agents unfettered access to diverse "
                    "third-party tool endpoints remain poorly understood. We present the first systematic security study of "
                    "the MCP ecosystem, comprising: (1) a six-surface attack taxonomy derived from auditing 30+ MCP server "
                    "implementations and discovering 2 original CVEs; (2) an automated large-scale scan of 620 packages using "
                    "46 custom Semgrep rules, revealing a path traversal hit rate of approximately 3%; and (3) a five-level "
                    "defense maturity framework with quantitative coverage analysis. Key findings: MCP Inspector implementations "
                    "exposing servers on 0.0.0.0 without authentication account for 2 confirmed CVEs; tool parameter injection "
                    "is the most prevalent attack surface; automated scanning found zero undisclosed high-severity vulnerabilities, "
                    "suggesting the ecosystem has matured but fundamental trust assumptions remain unresolved. We release all 46 "
                    "Semgrep rules and the 91-node MCP security knowledge graph as open-source artifacts.")
        self.multi_cell(self.pw, 5, abstract, align="J")
        self.ln(5)
        self.set_font(self.normal_font, "B", 9)
        self.set_text_color(60,60,60)
        self.multi_cell(self.pw, 5, "Keywords: Model Context Protocol, MCP security, LLM agent security, vulnerability taxonomy, large-scale scanning, Semgrep, CVE", align="C")
        self.ln(8)
        self.set_draw_color(180,180,180)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(5)


pdf = PaperPDF()
pdf.title_page()

lines = content.split('\n')
i = 0
# Skip title block, find Introduction
while i < len(lines):
    if lines[i].startswith('## 1. Introduction'):
        break
    i += 1

in_code = False
code_buf = []

while i < len(lines):
    line = lines[i]
    i += 1

    if line.strip() == '':
        continue

    if line.strip().startswith('```'):
        if in_code:
            pdf.code_block('\n'.join(code_buf))
            code_buf = []
            in_code = False
        else:
            in_code = True
        continue

    if in_code:
        code_buf.append(line)
        continue

    # Mermaid blocks - skip
    if line.strip().startswith('```mermaid'):
        while i < len(lines):
            if lines[i].strip().startswith('```'):
                i += 1
                break
            i += 1
        continue

    # Tables
    if '|' in line and line.strip().startswith('|'):
        table_rows = []
        skip_sep = False
        while i < len(lines) and '|' in lines[i]:
            cl = lines[i].strip()
            if re.match(r'^\|[\s\-:|]+\|$', cl):
                i += 1
                continue
            cells = [c.strip() for c in cl.split('|')[1:-1]]
            table_rows.append(cells)
            i += 1
        if table_rows:
            headers = table_rows[0] if len(table_rows) > 1 else table_rows[0]
            rows = table_rows[1:] if len(table_rows) > 1 else []
            ncols = len(headers)
            cw = pdf.pw / ncols
            pdf.mini_table(headers, rows, [cw] * ncols)
        continue

    # Headings
    if line.startswith('## '):
        pdf.h2(line[3:].strip())
    elif line.startswith('### '):
        pdf.h3(line[4:].strip())
    elif line.startswith('#### '):
        pdf.set_font(pdf.normal_font, "B", 10)
        pdf.set_text_color(60,60,60)
        pdf.multi_cell(pdf.pw, 5.5, line[5:].strip())
        pdf.ln(1)
    elif line.startswith('**Figure') or line.startswith('**Table'):
        pdf.set_font(pdf.normal_font, "", 9)
        pdf.set_text_color(60,60,60)
        pdf.multi_cell(pdf.pw, 5, line.strip(), align="C")
        pdf.ln(2)
    elif line.startswith('- **'):
        match = re.match(r'- \*\*(.+?)\*\*[:,]?\s*(.*)', line)
        if match:
            pdf.set_font(pdf.normal_font, "B", 10)
            pdf.set_text_color(20,20,20)
            pdf.cell(5, 5.2, "-")
            tw = pdf.get_string_width(match.group(1))
            pdf.cell(tw + 2, 5.2, match.group(1))
            pdf.set_font(pdf.normal_font, "", 10)
            pdf.multi_cell(pdf.pw - 5 - tw - 2, 5.2, match.group(2).strip(), align="L")
            pdf.set_x(pdf.l_margin)
        else:
            pdf.bullet(line[2:])
    elif line.startswith('- '):
        pdf.bullet(line[2:])
    elif re.match(r'^\d+\.\s', line):
        num = re.match(r'^(\d+)\.', line).group(1)
        pdf.numbered(num, line[line.index('.')+1:].strip())
    elif line.startswith('> '):
        pdf.set_font(pdf.normal_font, "I", 9)
        pdf.set_text_color(80,80,80)
        pdf.multi_cell(pdf.pw, 5, line[2:].strip())
        pdf.set_x(pdf.l_margin)
    elif line.startswith('---'):
        pdf.ln(2)
        pdf.set_draw_color(180,180,180)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(2)
    else:
        pdf.para(line)

pdf.output(OUTPUT_PDF)
import os
print(f"PDF: {OUTPUT_PDF}")
print(f"Pages: {pdf.page_no()}, Size: {os.path.getsize(OUTPUT_PDF)/1024:.1f} KB")
