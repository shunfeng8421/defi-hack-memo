"""Check all 3 Zenodo papers for formatting and encoding issues."""
import os

base = r"D:\ll\knowledge-base\10-security\zenodo-check"

# === PDF 1 ===
print("=" * 60)
print("PAPER 1: MCP Security Taxonomy")
print("=" * 60)
with open(os.path.join(base, "paper1.pdf"), "rb") as f:
    content = f.read()

valid = content[:5] == b"%PDF-"
print(f"Valid PDF: {valid}")
print(f"Size: {len(content)} bytes ({len(content)/1024:.1f} KB)")

# Check for Chinese font embedding
has_msyh = b"MSYH" in content or b"msyh" in content
has_yahei = b"YaHei" in content or b"Microsoft YaHei" in content
print(f"Chinese font (msyh): {has_msyh}")
print(f"Chinese font (YaHei): {has_yahei}")

# Count pages by counting /Type /Page entries
page_count = content.count(b"/Type /Page") - content.count(b"/Type /Pages")
print(f"Estimated pages: {page_count}")

# Check for problematic emoji replacements
print(f"Has [BYPASS] marker: {b'[BYPASS]' in content}")
print(f"Has [BLOCKED] marker: {b'[BLOCKED]' in content}")

# Check if PDF is actually a text-based PDF (not pure image)
has_text = b"BT" in content and b"ET" in content  # text blocks
print(f"Has text content: {has_text}")

print()

# === PDF 2 ===
print("=" * 60)
print("PAPER 2: Prompt Injection")
print("=" * 60)
with open(os.path.join(base, "paper2.pdf"), "rb") as f:
    content = f.read()

valid = content[:5] == b"%PDF-"
print(f"Valid PDF: {valid}")
print(f"Size: {len(content)} bytes ({len(content)/1024:.1f} KB)")

has_msyh = b"MSYH" in content or b"msyh" in content
has_yahei = b"YaHei" in content or b"Microsoft YaHei" in content
print(f"Chinese font (msyh): {has_msyh}")
print(f"Chinese font (YaHei): {has_yahei}")

page_count = content.count(b"/Type /Page") - content.count(b"/Type /Pages")
print(f"Estimated pages: {page_count}")
print(f"Has text content: {b'BT' in content and b'ET' in content}")

print()

# === CSV & README ===
print("=" * 60)
print("PAPER 3: DeFi Attack Dataset")
print("=" * 60)

# Check CSV encoding
with open(os.path.join(base, "hacks.csv"), "rb") as f:
    raw = f.read()

has_bom = raw[:3] == b'\xef\xbb\xbf'
print(f"CSV file size: {len(raw)} bytes ({len(raw)/1024:.1f} KB)")
print(f"UTF-8 BOM: {has_bom}")

# Try decoding
try:
    text = raw.decode('utf-8')
    lines = text.split('\n')
    print(f"CSV lines: {len(lines)}")
    print(f"CSV header: {lines[0]}")
    # Check first few data lines
    for i in range(1, 6):
        if i < len(lines) and lines[i].strip():
            fields = lines[i].split(',')
            cat = fields[2] if len(fields) > 2 else 'N/A'
            print(f"  Line {i}: name={fields[1] if len(fields)>1 else '?'}, category={cat}")
except Exception as e:
    print(f"UTF-8 decode failed: {e}")
    try:
        text = raw.decode('gbk')
        print("Decoded as GBK (first 200 chars):", text[:200])
    except:
        print("GBK decode also failed")

print()

# Check README
with open(os.path.join(base, "readme3.md"), "rb") as f:
    raw = f.read()

print(f"README size: {len(raw)} bytes")
text = raw.decode('utf-8')
print("README content:")
print(text)
print()

# Check for TBD placeholder
if "TBD" in text:
    print("WARNING: DOI placeholder 'TBD' found in README!")
if "shunfeng8421" in text:
    print("WARNING: Username 'shunfeng8421' used instead of real name 'Shiqiang Chen'!")
if "mit-license" in text or "MIT" in text:
    print("NOTE: License field OK (MIT)")
