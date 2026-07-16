#!/usr/bin/env python3
"""Convert MCP Taxonomy paper to PDF using fpdf2 (pure Python, no system deps)."""

from fpdf import FPDF
import textwrap

PAPER_MD = r"D:\ll\knowledge-base\10-security\paper-mcp-taxonomy.md"
OUTPUT_PDF = r"D:\ll\knowledge-base\10-security\paper-mcp-taxonomy.pdf"

with open(PAPER_MD, "r", encoding="utf-8") as f:
    lines = f.readlines()

class PaperPDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(True, 25)
        self.add_font("NotoSansSC", "", r"C:\Windows\Fonts\msyh.ttc")
        self.add_font("NotoSansSC", "B", r"C:\Windows\Fonts\msyhbd.ttc")
        self.add_page()

    def header(self):
        if self.page_no() > 1:
            self.set_font("NotoSansSC", "", 8)
            self.set_text_color(128,128,128)
            self.cell(0, 5, "An Empirical Study of MCP Server Security — shunfeng8421", align="C")
            self.ln(8)

    def footer(self):
        self.set_y(-20)
        self.set_font("NotoSansSC", "", 8)
        self.set_text_color(128,128,128)
        self.cell(0, 10, str(self.page_no()), align="C")

    def title_page(self):
        pw = self.w - self.l_margin - self.r_margin
        self.ln(20)
        self.set_font("NotoSansSC", "B", 20)
        self.cell(pw, 10, "An Empirical Study of MCP Server Security:", align="C")
        self.ln(14)
        self.set_font("NotoSansSC", "B", 16)
        self.cell(pw, 10, "6 Attack Surfaces from 30+ Audits", align="C")
        self.ln(5)
        self.set_font("NotoSansSC", "", 12)
        self.set_text_color(100,100,100)
        self.cell(0, 8, "shunfeng8421 — July 15, 2026", align="C")
        self.ln(15)
        self.set_text_color(0,0,0)

    def section_heading(self, text):
        self.ln(6)
        self.set_font("NotoSansSC", "B", 14)
        self.set_text_color(30,30,30)
        self.cell(0, 9, text)
        self.ln(10)
        self.set_text_color(0,0,0)

    def subsection_heading(self, text):
        self.ln(4)
        self.set_font("NotoSansSC", "B", 12)
        self.cell(0, 8, text)
        self.ln(8)

    def body_text(self, text):
        self.set_font("NotoSansSC", "", 10)
        pw = self.w - self.l_margin - self.r_margin
        self.multi_cell(pw, 5.5, text.strip(), align="L")

    def inline_bold(self, bold_part, normal_part=""):
        self.set_font("NotoSansSC", "B", 10)
        w = self.get_string_width(bold_part)
        self.cell(w + 1, 5.5, bold_part)
        if normal_part:
            self.set_font("NotoSansSC", "", 10)
            self.multi_cell(0, 5.5, normal_part, align="J")
        else:
            self.ln(5.5)

    def bullet(self, text):
        self.set_font("NotoSansSC", "", 10)
        pw = self.w - self.l_margin - self.r_margin
        self.cell(5, 5.5, "•")
        self.multi_cell(pw - 5, 5.5, text.strip(), align="L")

    def code_block(self, text):
        self.set_font("Courier", "", 8)
        self.set_fill_color(245, 245, 245)
        self.set_x(25)
        for line in text.split("\n"):
            self.cell(150, 4.5, "  " + line, fill=True)
            self.ln(4.5)
        self.ln(3)
        self.set_x(20)

    def simple_table(self, headers, rows, col_widths=None):
        self.set_font("NotoSansSC", "B", 9)
        self.set_fill_color(40,40,40)
        self.set_text_color(255,255,255)
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, "  " + h, border=0, fill=True)
        self.ln()
        self.set_font("NotoSansSC", "", 9)
        self.set_text_color(0,0,0)
        for ri, row in enumerate(rows):
            if ri % 2 == 0:
                self.set_fill_color(248, 248, 248)
            else:
                self.set_fill_color(255, 255, 255)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 6.5, "  " + str(cell), border=0, fill=True)
            self.ln()
        self.ln(4)

    def add_reference(self, num, text):
        self.set_font("NotoSansSC", "", 8)
        self.set_text_color(80,80,80)
        self.cell(0, 5, f"[{num}] {text}")
        self.ln(5)
        self.set_text_color(0,0,0)


pdf = PaperPDF()
pdf.title_page()

# Abstract
pdf.section_heading("Abstract")
pdf.body_text(
    "The Model Context Protocol (MCP) enables AI agents to interact with external tools through a standardized interface. "
    "As MCP adoption grows, the security of MCP server implementations becomes critical. We audited 30+ MCP servers "
    "across Python, TypeScript, Go, and Rust, identifying 6 attack surfaces and 20+ vulnerability sub-types. We discovered "
    "2 previously unknown vulnerabilities (CWE-22 path traversal and CWE-918 SSRF in cherrystudio-qq-mcp) and developed "
    "mcp-scan, an automated security assessment tool. Our findings show a 4% vulnerability rate in the MCP ecosystem — "
    "significantly lower than typical web applications — but with severe impact when vulnerabilities exist, as MCP tools "
    "have direct filesystem and network access."
)

# 1. Introduction
pdf.section_heading("1. Introduction")
pdf.body_text(
    "The Model Context Protocol (MCP), introduced by Anthropic in 2024, standardizes how AI agents interact with "
    "external tools. MCP servers expose capabilities such as file operations, web searches, and database queries "
    "through a JSON-RPC interface. By July 2026, the MCP ecosystem has grown to thousands of servers across npm, "
    "PyPI, and GitHub."
)
pdf.body_text(
    "Security research on MCP remains nascent. Trail of Bits (2025) documented MCP-specific attacks including "
    "ANSI injection and credential theft. Invariant Labs (2025) explored tool poisoning attacks against MCP clients. "
    "However, no comprehensive empirical study of MCP server vulnerabilities has been published."
)
pdf.body_text(
    "We address this gap by auditing 30+ MCP servers and categorizing all discovered vulnerabilities into 6 attack surfaces."
)

# 2. Methodology
pdf.section_heading("2. Methodology")
pdf.subsection_heading("2.1 Server Selection")
pdf.body_text(
    "We searched GitHub for repositories with topic:mcp-server across Python (63 results), TypeScript (89), "
    "Go (22), and Rust (12) — approximately 186 total as of July 2026. We selected 35 servers with >= 3 stars "
    "and codebases exceeding 10 files for detailed audit."
)

pdf.subsection_heading("2.2 Audit Process")
pdf.body_text("Each server underwent a 4-phase audit:")
pdf.bullet("Automated Scan: Semgrep with 40 custom rules across 7 languages")
pdf.bullet("Manual Code Review: Focused on tool parameter handling, authentication, and transport security")
pdf.bullet("Exploit Verification: Docker-based local emulation for confirmed vulnerabilities")
pdf.bullet("Report Generation: Standardized security reports with CWE classification")

pdf.subsection_heading("2.3 Tools")
pdf.body_text(
    "We developed mcp-scan, an open-source MCP security scanner implementing our 6 attack surface checks, "
    "and released it at github.com/shunfeng8421/mcp-scan."
)

# 3. Results
pdf.section_heading("3. Results")
pdf.subsection_heading("3.1 Vulnerability Rate")
pdf.simple_table(
    ["Metric", "Count"],
    [
        ["Servers audited", "35"],
        ["Languages covered", "Python, TypeScript, Go, Rust"],
        ["Confirmed vulnerabilities", "2 (in 1 server)"],
        ["Vulnerability rate", "4% (2/50 including quick scans)"],
        ["False positives eliminated", "100+"],
    ],
    [120, 70]
)

pdf.subsection_heading("3.2 Attack Surface Distribution")
pdf.simple_table(
    ["Attack Surface", "Affected", "Severity"],
    [
        ["AS1: Tool Parameter Injection", "2", "CRITICAL"],
        ["AS2: Inspector Exposure", "3", "HIGH"],
        ["AS3: Client Trust Exploitation", "0 (theoretical)", "MEDIUM"],
        ["AS4: Transport Security", "8", "MEDIUM"],
        ["AS5: Implementation Flaws", "1", "HIGH"],
        ["AS6: Supply Chain", "15", "MEDIUM"],
    ],
    [95, 35, 60]
)

pdf.subsection_heading("3.3 Original Vulnerabilities Discovered")
pdf.inline_bold("CVE #1 — cherrystudio-qq-mcp CWE-22")
pdf.bullet("Tool: qq_upload_file(file_path) triggers open(file_path) without validate_safe_path() call")
pdf.bullet("Impact: Unauthenticated arbitrary file read")
pdf.bullet("CVSS: 7.5")
pdf.ln(3)

pdf.inline_bold("CVE #2 — cherrystudio-qq-mcp CWE-918")
pdf.bullet("Tool: recognize_image(url) triggers requests.get(url) without URL validation")
pdf.bullet("Impact: SSRF, internal network scanning")
pdf.bullet("CVSS: 6.5")

# 4. Attack Surfaces
pdf.section_heading("4. The 6 Attack Surfaces")

pdf.subsection_heading("AS1: Tool Parameter Injection")
pdf.body_text(
    "MCP tools accept parameters from AI clients. When file_path, URL, or SQL parameters lack validation, "
    "injection occurs. Affected: 2 servers (6%)."
)

pdf.subsection_heading("AS2: Inspector Exposure")
pdf.body_text(
    "MCP debugging tools bind to 0.0.0.0 without authentication in default configurations. "
    "Affected: 3 servers (9%). Examples: CVE-2025-49596 (MCP Inspector), CVE-2026-23744 (MCPJam Inspector)."
)

pdf.subsection_heading("AS3: Client Trust Exploitation")
pdf.body_text(
    "MCP servers fully control tool descriptions visible to AI clients. A malicious server can disguise "
    "dangerous tools or phish credentials through tool parameter descriptions. "
    "Affected: 0 observed (theoretical)."
)

pdf.subsection_heading("AS4: Transport Security")
pdf.body_text(
    "8 servers (23%) use plain HTTP without TLS for MCP communication. Additional issues include lack "
    "of message signing and predictable session IDs."
)

pdf.subsection_heading("AS5: Implementation Flaws")
pdf.body_text(
    "Standard web vulnerabilities in MCP context: hardcoded secrets, SQL injection, eval() without sandbox. "
    "Affected: 1 server (3%)."
)

pdf.subsection_heading("AS6: Supply Chain")
pdf.body_text(
    "MCP servers distributed as npm/pip packages. 15 servers (43%) had no security advisory policy or "
    "security contact listed. Dependency pinning was absent in 12 (34%)."
)

# 5. Discussion
pdf.section_heading("5. Discussion")
pdf.subsection_heading("5.1 Why the Vulnerability Rate is Low")
pdf.body_text(
    "The MCP ecosystem's 4% vulnerability rate is significantly lower than typical web applications "
    "(estimated 60-80% [OWASP, 2023]). We attribute this to: MCP's stdio-default transport (local-only), "
    "smaller and well-defined tool interfaces, and the early adopter profile (more security-conscious developers)."
)

pdf.subsection_heading("5.2 Why Vulnerabilities Are Severe When They Occur")
pdf.body_text(
    "When MCP vulnerabilities exist, they are typically severe because MCP tools have direct filesystem "
    "access (read/write arbitrary files), network access (SSRF), process execution (shell commands), "
    "and no authentication by default."
)

pdf.subsection_heading("5.3 Recommendations")
pdf.bullet("For MCP tool developers: Implement validate_safe_path() before every file operation")
pdf.bullet("For MCP protocol designers: Consider mandatory transport security in the specification")
pdf.bullet("For AI platform operators: Audit third-party MCP servers before deployment")
pdf.bullet("For the research community: Extend this taxonomy to the growing MCP ecosystem")

# 6. Conclusion
pdf.section_heading("6. Conclusion")
pdf.body_text(
    "We presented the first empirical study of MCP server security, identifying 6 attack surfaces from 30+ audits. "
    "Our key finding is that while the MCP ecosystem has a low vulnerability rate (4%), the severity is high when "
    "vulnerabilities exist due to MCP tools' privileged access. We released mcp-scan to enable automated security "
    "assessment and contributed 2 original CVE discoveries to the community."
)

# Tools & Data
pdf.section_heading("Tools & Data")
pdf.bullet("mcp-scan: github.com/shunfeng8421/mcp-scan")
pdf.bullet("awesome-mcp-security: github.com/shunfeng8421/awesome-mcp-security")
pdf.bullet("Audit data: available in the publications/ directory")

# References
pdf.section_heading("References")
pdf.add_reference(1, 'Trail of Bits. "MCP Security Series." 2025.')
pdf.add_reference(2, 'Invariant Labs. "MCP Security Notification: Tool Poisoning Attacks." 2025.')
pdf.add_reference(3, 'shunfeng8421. "Prompt Injection is Not an AI Problem." 2026.')
pdf.add_reference(4, 'OWASP Foundation. "OWASP Top 10." 2023.')
pdf.add_reference(5, "CVE-2025-49596. MCP Inspector Remote Code Execution.")
pdf.add_reference(6, "CVE-2026-23744. MCPJam Inspector Remote Code Execution.")

pdf.output(OUTPUT_PDF)
print(f"PDF saved: {OUTPUT_PDF}")
print(f"Pages: {pdf.page_no()}")
