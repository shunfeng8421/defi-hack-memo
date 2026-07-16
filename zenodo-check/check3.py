"""CSV analysis."""
from collections import Counter

with open(r"D:\ll\knowledge-base\10-security\zenodo-check\hacks.csv", "rb") as f:
    raw = f.read()

text = raw.decode('utf-8')
lines = text.split('\n')

cats = Counter()
for line in lines[1:]:
    if ',' in line:
        parts = line.split(',')
        if len(parts) >= 3:
            cat = parts[2].strip()
            if cat:
                cats[cat] += 1

print("=== Category Distribution ===")
for cat, count in cats.most_common():
    print(f"  {cat}: {count}")

print(f"\nTotal records: {sum(cats.values())}")
print(f"Unique categories: {len(cats)}")

has_bom = raw[:3] == b'\xef\xbb\xbf'
print(f"\nUTF-8 BOM: {has_bom}")
print("NOTE: Without BOM, Excel on Windows shows Chinese as garbled text")
