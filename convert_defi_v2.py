#!/usr/bin/env python3
"""Convert expanded DeFi paper to PDF for Zenodo v2.0.0."""
from fpdf import FPDF
import re, textwrap

INPUT_MD = r"D:\ll\knowledge-base\10-security\paper\03-defi-evolution\EN.md"
OUTPUT_PDF = r"D:\ll\knowledge-base\10-security\paper-deFi-v2.pdf"

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
            self.cell(0, 4, "DEFIHACK-824: A Multi-Source Verified Dataset of DeFi Security Incidents — Shiqiang Chen", align="C")
            self.ln(6)

    def footer(self):
        self.set_y(-18)
        self.set_font(self.normal_font, "", 7)
        self.set_text_color(128,128,128)
        self.cell(0, 8, str(self.page_no()), align="C")

    def h1(self, text):
        self.ln(6)
        self.set_font(self.normal_font, "B", 16)
        self.set_text_color(0,0,0)
        self.multi_cell(self.pw, 8, text, align="L")
        self.ln(2)

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

    def bold_para(self, text):
        self.set_font(self.normal_font, "B", 10)
        self.set_text_color(20,20,20)
        self.multi_cell(self.pw, 5.2, text.strip(), align="L")

    def bullet(self, text):
        self.set_font(self.normal_font, "", 10)
        self.set_text_color(20,20,20)
        x = self.get_x()
        self.cell(6, 5.2, "-")
        self.multi_cell(self.pw - 6, 5.2, text.strip(), align="L")
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

    def meta_text(self, text):
        self.set_font(self.normal_font, "", 9)
        self.set_text_color(100,100,100)
        self.multi_cell(self.pw, 5, text.strip(), align="C")

    def title_page(self):
        self.ln(15)
        # Title
        self.set_font(self.normal_font, "B", 16)
        self.set_text_color(0,0,0)
        self.multi_cell(self.pw, 8, "Evolving Threats, Shifting Patterns:\nA Multi-Source Verified Dataset and Statistical\nAnalysis of 823 DeFi Security Incidents (2017-2026)", align="C")
        self.ln(5)
        # Author
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
        abstract = ("Decentralized Finance (DeFi) has suffered over $5 billion in cumulative losses from security incidents, "
                    "yet the academic community lacks a large-scale, multi-source-verified dataset to systematically characterize "
                    "these threats. We present DEFIHACK-824, a curated dataset of 823 DeFi security incidents spanning 2017 to 2026, "
                    "cross-validated against three independent intelligence sources (Rekt News, SlowMist, and CertiK). Each record is "
                    "annotated with attack category, confidence level, and estimated financial loss. We classify incidents into 14 attack "
                    "categories and conduct statistical analyses revealing that flash-loan-enabled price manipulation and reentrancy together "
                    "account for 51.5% of all attacks. A chi-squared test rejects the null hypothesis of uniform category distribution at "
                    "p < 0.0001 (chi-squared = 1,273.2, df = 13). Despite widespread deployment of automated detection tools, the annual "
                    "attack count has not monotonically decreased, suggesting adaptive attacker strategies that outpace rule-based defenses. "
                    "We further propose a six-layer DeFi threat model and quantify the effectiveness of four defense classes against the "
                    "observed attack distribution. The dataset, threat model, and 50 categorized Solidity vulnerability patterns are released "
                    "under the MIT license.")
        self.multi_cell(self.pw, 5, abstract, align="J")
        self.ln(5)
        self.set_font(self.normal_font, "B", 9)
        self.set_text_color(60,60,60)
        self.multi_cell(self.pw, 5, "Keywords: DeFi security, vulnerability dataset, smart contract audit, threat modeling, statistical analysis, flash loan attack, reentrancy", align="C")
        self.ln(8)
        self.set_draw_color(180,180,180)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(5)


pdf = PaperPDF()
pdf.title_page()

# Parse and render sections
lines = content.split('\n')
i = 0
in_code = False
code_buf = []
in_table = False
table_rows = []
table_align = []
skip_until = -1

# Skip the title block (already rendered on title page)
# Find where Introduction starts
while i < len(lines):
    if lines[i].startswith('## 1. Introduction'):
        break
    i += 1

while i < len(lines):
    line = lines[i]
    i += 1

    # Skip empty lines
    if line.strip() == '':
        continue

    # Code blocks
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
        if not in_table:
            in_table = True
            table_rows = []
            # Check if separator row
            if re.match(r'^\|[\s\-:|]+\|$', line.strip()):
                continue
        # Check if separator row
        if re.match(r'^\|[\s\-:|]+\|$', line.strip()):
            continue
        cells = [c.strip() for c in line.strip().split('|')[1:-1]]
        table_rows.append(cells)

        # Check if next line continues the table
        if i >= len(lines) or '|' not in lines[i]:
            in_table = False
            if table_rows:
                headers = table_rows[0]
                rows = table_rows[1:]
                ncols = len(headers)
                cw = min(50, pdf.pw / ncols)
                pdf.mini_table(headers, rows, [cw] * ncols)
            table_rows = []
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
    elif line.startswith('**Figure'):
        pdf.set_font(pdf.normal_font, "B", 9)
        pdf.set_text_color(100,100,100)
        pdf.multi_cell(pdf.pw, 5, line.strip(), align="C")
        pdf.ln(2)
    elif line.startswith('**Table'):
        pdf.set_font(pdf.normal_font, "B", 9)
        pdf.set_text_color(60,60,60)
        pdf.multi_cell(pdf.pw, 5, line.strip(), align="C")
        pdf.ln(2)
    elif line.startswith('- **'):
        # Bold bullet: - **Term**: definition
        match = re.match(r'- \*\*(.+?)\*\*[:,]?\s*(.*)', line)
        if match:
            pdf.set_font(pdf.normal_font, "B", 10)
            pdf.set_text_color(20,20,20)
            x = pdf.get_x()
            pdf.cell(5, 5.2, "-")
            term_w = pdf.get_string_width(match.group(1))
            pdf.cell(term_w + 2, 5.2, match.group(1))
            pdf.set_font(pdf.normal_font, "", 10)
            pdf.multi_cell(pdf.pw - 5 - term_w - 2, 5.2, match.group(2).strip(), align="L")
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
print(f"PDF generated: {OUTPUT_PDF}")
print(f"Pages: {pdf.page_no()}")

import os
size_kb = os.path.getsize(OUTPUT_PDF) / 1024
print(f"Size: {size_kb:.1f} KB")
