# -*- coding: utf-8 -*-
"""Regenerate all 16 dirty PDFs from the already-fixed HTML files via headless Chrome."""
import subprocess, os, time

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ROOT = r"D:\ll\knowledge-base\10-security"

# (html_path, pdf_path) pairs — all relative to ROOT
JOBS = [
    ("paper-mcp-taxonomy-v2.html", "paper-mcp-taxonomy-v2.pdf"),
    ("paper-deFi-v2.html", "paper-deFi-v2.pdf"),
    (r"paper\02-mcp-taxonomy\EN.html", r"paper\02-mcp-taxonomy\EN.pdf"),
    (r"paper\03-defi-evolution\EN.html", r"paper\03-defi-evolution\EN.pdf"),
    (r"paper\04-decade-analysis\EN.html", r"paper\04-decade-analysis\EN.pdf"),
    (r"paper\04-decade-analysis\CN.html", r"paper\04-decade-analysis\CN.pdf"),
    (r"paper\05-flash-loan-evolution\EN.html", r"paper\05-flash-loan-evolution\EN.pdf"),
    (r"paper\05-flash-loan-evolution\CN.html", r"paper\05-flash-loan-evolution\CN.pdf"),
    (r"paper\06-taxonomy\EN.html", r"paper\06-taxonomy\EN.pdf"),
    (r"paper\06-taxonomy\CN.html", r"paper\06-taxonomy\CN.pdf"),
    (r"paper\07-hardening-gradient\EN.html", r"paper\07-hardening-gradient\EN.pdf"),
    (r"paper\07-hardening-gradient\CN.html", r"paper\07-hardening-gradient\CN.pdf"),
    (r"paper\08-eip712-errors\EN.html", r"paper\08-eip712-errors\EN.pdf"),
    (r"paper\08-eip712-errors\CN.html", r"paper\08-eip712-errors\CN.pdf"),
    (r"paper\09-ai-agent-defi\EN.html", r"paper\09-ai-agent-defi\EN.pdf"),
    (r"paper\09-ai-agent-defi\CN.html", r"paper\09-ai-agent-defi\CN.pdf"),
]

ok, fail = 0, 0
for html_rel, pdf_rel in JOBS:
    html_abs = os.path.join(ROOT, html_rel)
    pdf_abs = os.path.join(ROOT, pdf_rel)
    if not os.path.exists(html_abs):
        print("MISSING HTML: %s" % html_rel)
        fail += 1
        continue
    url = "file:///" + html_abs.replace("\\", "/")
    cmd = [
        CHROME, "--headless", "--disable-gpu",
        "--no-pdf-header-footer",
        "--print-to-pdf=%s" % pdf_abs,
        url,
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=120)
    if os.path.exists(pdf_abs) and os.path.getmtime(pdf_abs) > time.time() - 60:
        size = os.path.getsize(pdf_abs)
        print("OK  %-45s %8d bytes" % (pdf_rel, size))
        ok += 1
    else:
        print("FAIL %s\n%s" % (pdf_rel, r.stderr.decode("utf-8", "ignore")[:300]))
        fail += 1

print("\n=== done: %d ok, %d fail ===" % (ok, fail))
