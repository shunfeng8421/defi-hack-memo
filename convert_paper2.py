#!/usr/bin/env python3
"""Convert Prompt Injection paper to PDF for Hugging Face Papers."""

from fpdf import FPDF

INPUT_MD = r"D:\ll\knowledge-base\10-security\paper-prompt-injection.tex.txt"
OUTPUT_PDF = r"D:\ll\knowledge-base\10-security\paper-prompt-injection.pdf"

with open(INPUT_MD, "r", encoding="utf-8") as f:
    lines = f.readlines()

class PaperPDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(True, 25)
        self.add_font("NotoSansSC", "", r"C:\Windows\Fonts\msyh.ttc")
        self.add_font("NotoSansSC", "B", r"C:\Windows\Fonts\msyhbd.ttc")
        self.add_page()
        self.pw = self.w - self.l_margin - self.r_margin

    def header(self):
        if self.page_no() > 1:
            self.set_font("NotoSansSC", "", 8)
            self.set_text_color(128,128,128)
            self.cell(0, 5, "Prompt Injection is Not an AI Problem — shunfeng8421", align="C")
            self.ln(8)

    def footer(self):
        self.set_y(-20)
        self.set_font("NotoSansSC", "", 8)
        self.set_text_color(128,128,128)
        self.cell(0, 10, str(self.page_no()), align="C")

    def title_page(self):
        self.ln(20)
        self.set_font("NotoSansSC", "B", 18)
        self.cell(self.pw, 10, "Prompt Injection is Not an AI Problem:", align="C")
        self.ln(12)
        self.cell(self.pw, 10, "Why MCP Tool Hardening Matters", align="C")
        self.ln(8)
        self.set_font("NotoSansSC", "", 11)
        self.set_text_color(100,100,100)
        self.cell(self.pw, 8, "shunfeng8421 — July 14, 2026 — cs.CR / cs.AI", align="C")
        self.ln(15)
        self.set_text_color(0,0,0)

    def section_heading(self, text):
        self.ln(5)
        self.set_font("NotoSansSC", "B", 13)
        self.cell(0, 9, text)
        self.ln(9)

    def subsection_heading(self, text):
        self.ln(3)
        self.set_font("NotoSansSC", "B", 11)
        self.cell(0, 7, text)
        self.ln(7)

    def body_text(self, text, bold=False):
        self.set_font("NotoSansSC", "B" if bold else "", 10)
        self.multi_cell(self.pw, 5.5, text.strip(), align="L")

    def bullet(self, text, bold_prefix=""):
        self.set_font("NotoSansSC", "", 10)
        self.cell(5, 5.5, "•")
        if bold_prefix:
            self.set_font("NotoSansSC", "B", 10)
            w = self.get_string_width(bold_prefix)
            self.cell(w, 5.5, bold_prefix)
            self.set_font("NotoSansSC", "", 10)
            self.multi_cell(self.pw - 5 - w, 5.5, text.strip(), align="L")
        else:
            self.multi_cell(self.pw - 5, 5.5, text.strip(), align="L")

    def table(self, headers, rows, col_widths):
        self.set_font("NotoSansSC", "B", 9)
        self.set_fill_color(40,40,40)
        self.set_text_color(255,255,255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, "  " + h, fill=True)
        self.ln()
        self.set_font("NotoSansSC", "", 9)
        self.set_text_color(0,0,0)
        for ri, row in enumerate(rows):
            if ri % 2 == 0:
                self.set_fill_color(245,245,245)
            else:
                self.set_fill_color(255,255,255)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 6.5, "  " + str(cell), fill=True)
            self.ln()
        self.ln(4)

    def separator(self):
        self.ln(2)
        self.set_draw_color(180,180,180)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)


pdf = PaperPDF()
pdf.title_page()

i = 0
while i < len(lines):
    line = lines[i].rstrip()

    # Skip separators
    if line.strip() == "---" or line.strip().startswith("---") and len(line.strip()) <= 3:
        pdf.separator()
        i += 1
        continue

    # Title (starting with #)
    if line.startswith("# "):
        pdf.title_page()
        i += 1
        continue

    # Section headings
    if line.startswith("## "):
        text = line[3:].strip()
        pdf.section_heading(text)
        i += 1
        continue

    if line.startswith("### "):
        text = line[4:].strip()
        pdf.subsection_heading(text)
        i += 1
        continue

    # Bold text (Author, classification line)
    if line.startswith("**"):
        text = line.replace("**", "").strip()
        pdf.body_text(text, bold=True)
        i += 1
        continue

    # Bullet (numbered)
    if line.strip() and (line.strip()[0].isdigit() and "." in line.strip()[:3]):
        text = line.strip()
        # Split at first dot-space
        if ". " in text:
            parts = text.split(". ", 1)
            prefix = parts[0] + ". "
            rest = parts[1]
            pdf.bullet(rest, bold_prefix=prefix)
        else:
            pdf.bullet(text)
        i += 1
        continue

    # Bullet (dash)
    if line.strip().startswith("- ") or line.strip().startswith("* "):
        text = line.strip()[2:]
        pdf.bullet(text)
        i += 1
        continue

    # Tables
    if "|" in line and line.strip().startswith("|"):
        table_lines = []
        while i < len(lines) and "|" in lines[i]:
            table_lines.append(lines[i].strip())
            i += 1

        if len(table_lines) >= 3:
            # Parse header
            header = [c.strip() for c in table_lines[0].strip("|").split("|")]
            # Skip separator line
            rows = []
            for tl in table_lines[2:]:
                cells = [c.strip().replace('\U0001f525','[BYPASS]').replace('\u2705','[BLOCKED]') for c in tl.strip("|").split("|")]
                rows.append(cells)

            n = len(header)
            cw = (pdf.pw - 10) / n
            pdf.table(header, rows, [cw] * n)
        continue

    # Regular paragraph
    if line.strip():
        pdf.body_text(line.strip())

    i += 1

pdf.output(OUTPUT_PDF)
print(f"PDF saved: {OUTPUT_PDF}")
print(f"Pages: {pdf.page_no()}")
