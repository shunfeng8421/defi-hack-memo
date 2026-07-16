"""Continue fixing - metadata already updated on draft 21383211."""
import os, sys, requests

sys.stdout.reconfigure(encoding='utf-8')
TOKEN = "3dMUkBYgFJRhuDygUbA5CONFZAcYzdxcWAVZgOEwjQMzaliayQZF2vD0uTQc"
BASE = "https://zenodo.org/api"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
NEW_ID = "21383211"
BUCKET = "https://zenodo.org/api/files/0b706a3b-1bac-4c3a-a3da-84a74f0102eb"

# Step 3: Delete old files
print("Step 3: Delete old files")
r = requests.get(f"{BASE}/deposit/depositions/{NEW_ID}", headers=HEADERS)
dep = r.json()
for f in dep.get("files", []):
    fid = f["id"]
    fname = f["filename"]
    print(f"  Deleting: {fname}...")
    r = requests.delete(f"{BASE}/deposit/depositions/{NEW_ID}/files/{fid}", headers=HEADERS)
    print(f"    {'OK' if r.status_code == 204 else f'Failed: {r.status_code}'}")

# Step 4: Upload fixed files
print()
print("Step 4: Upload fixed files")

# README
readme = """# DeFi Attack Evolution Dataset (824 Cases, 2017-2026)

## Files
- `hacks-verified.csv` -- 824 classified DeFi attacks with year, name, category, loss
- `verified-100.csv` -- 100 manually verified cases with deep classification

## Metadata
- Source: DeFiHackLabs PoC reproductions
- Cross-validated: Rekt News, SlowMist, CertiK
- Ground-truth labels: 50 cases confirmed by 2+ independent sources
- Classification: 14 categories (keyword-based + manual verification)
- Total: 824 incidents, 2017-2026

## Citation
```
@misc{chen-defi-attacks-2026,
  author = {Shiqiang Chen},
  title = {DeFi Attack Evolution Dataset: 824 Security Incidents (2017--2026)},
  year = {2026},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.21382533}
}
```

## License
MIT -- free to use with attribution
"""

print("  Uploading README.md...")
r = requests.put(f"{BUCKET}/README.md", data=readme.encode('utf-8'), headers={"Authorization": f"Bearer {TOKEN}"})
print(f"    {'OK' if r.status_code == 200 else f'Failed: {r.status_code}'}")

# CSV with BOM
csv_path = r"D:\ll\knowledge-base\10-security\zenodo-check\hacks.csv"
with open(csv_path, "rb") as f:
    csv_data = f.read()
if csv_data[:3] != b'\xef\xbb\xbf':
    csv_data = b'\xef\xbb\xbf' + csv_data
    print("  CSV: BOM added")

print("  Uploading hacks-verified.csv...")
r = requests.put(f"{BUCKET}/hacks-verified.csv", data=csv_data, headers={"Authorization": f"Bearer {TOKEN}"})
print(f"    {'OK' if r.status_code == 200 else f'Failed: {r.status_code}'}")

# Verified-100
csv100_path = r"D:\ll\knowledge-base\10-security\zenodo-check\verified-100.csv"
with open(csv100_path, "rb") as f:
    csv100_data = f.read()
if csv100_data[:3] != b'\xef\xbb\xbf':
    csv100_data = b'\xef\xbb\xbf' + csv100_data

print("  Uploading verified-100.csv...")
r = requests.put(f"{BUCKET}/verified-100.csv", data=csv100_data, headers={"Authorization": f"Bearer {TOKEN}"})
print(f"    {'OK' if r.status_code == 200 else f'Failed: {r.status_code}'}")

# Step 5: Publish
print()
print("Step 5: Publish new version")
r = requests.post(f"{BASE}/deposit/depositions/{NEW_ID}/actions/publish", headers=HEADERS)
if r.status_code == 202:
    pub = r.json()
    print(f"PUBLISHED!")
    print(f"Version DOI: {pub['doi']}")
    print(f"Concept DOI: https://doi.org/{pub['conceptdoi']}")
    print(f"Page: https://zenodo.org/records/{NEW_ID}")
else:
    print(f"Failed: {r.status_code} - {r.text}")
