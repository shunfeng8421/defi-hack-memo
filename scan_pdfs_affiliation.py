# -*- coding: utf-8 -*-
"""Scan all PDFs for the false affiliation text."""
import os, glob

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

TARGETS = [
    "Institute of Information Engineering",
    "Chinese Academy of Sciences",
    "IIE, CAS",
]
# CJK targets (PDF text extraction may or may not capture CJK)
CJK_TARGETS = ["中国科学院", "信息工程研究所"]

root = r"D:\ll\knowledge-base\10-security"
pdfs = glob.glob(os.path.join(root, "**", "*.pdf"), recursive=True)

dirty = []
for pdf_path in sorted(pdfs):
    rel = os.path.relpath(pdf_path, root)
    if "figures" in rel:
        continue
    try:
        reader = PdfReader(pdf_path)
        # Title page is enough, but scan first 3 pages to be safe
        text = ""
        for page in reader.pages[:3]:
            text += page.extract_text() or ""
        found = [t for t in TARGETS + CJK_TARGETS if t in text]
        if found:
            dirty.append((rel, found))
            print("DIRTY: %s -> %s" % (rel, found))
        else:
            print("clean: %s" % rel)
    except Exception as e:
        print("ERROR: %s -> %s" % (rel, e))

print("\n=== SUMMARY: %d dirty PDFs ===" % len(dirty))
for rel, found in dirty:
    print("  " + rel)
