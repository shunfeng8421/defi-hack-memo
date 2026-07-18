"""Fix Paper 3 on Zenodo using new version flow."""
import json, os, sys, requests
from urllib.request import urlretrieve

sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.environ.get("ZENODO_TOKEN", "")
BASE = "https://zenodo.org/api"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
DEP_ID = "21382533"

# Step 1: Create new version
print("=" * 60)
print("Step 1: Create new version draft")
print("=" * 60)
r = requests.post(f"{BASE}/deposit/depositions/{DEP_ID}/actions/newversion", headers=HEADERS)
if r.status_code == 201:
    new_dep = r.json()
    new_id = new_dep["id"]
    bucket_url = new_dep["links"]["bucket"]
    print(f"New draft ID: {new_id}")
    print(f"Bucket: {bucket_url}")
else:
    print(f"FAILED: {r.status_code} - {r.text}")
    sys.exit(1)

# Step 2: Update metadata
print()
print("=" * 60)
print("Step 2: Update metadata (author name etc.)")
print("=" * 60)
r = requests.put(
    f"{BASE}/deposit/depositions/{new_id}",
    headers=HEADERS,
    json={"metadata": {
        "title": "DeFi Attack Evolution Dataset (824 Cases, 2017-2026)",
        "creators": [{"name": "Shiqiang Chen", "affiliation": "Independent Researcher"}],
        "description": "A comprehensive dataset of 824 DeFi security incidents from 2017 to 2026. Each record includes year, project name, attack category, loss amount, and chain. 50 cases are ground-truth verified by 2+ independent sources (Rekt News, SlowMist, CertiK). Categories span flash loan attacks, reentrancy, permission bugs, price manipulation, bridge exploits, governance attacks, and more. Suitable for ML training, trend analysis, and security research.",
        "access_right": "open",
        "license": "mit-license",
        "upload_type": "dataset",
        "keywords": ["DeFi security", "smart contract audit", "blockchain attacks", "crypto hacks", "Web3 security", "flash loan", "reentrancy", "MEV"],
        "publication_date": "2026-07-15",
        "notes": "Version 1.0.1. Fixed: author name, DOI in README, CSV UTF-8 BOM for Excel compatibility. Dataset compiled from DeFiHackLabs PoC reproductions and cross-validated with Rekt News, SlowMist Hacked Archive, and CertiK alerts."
    }}
)
if r.status_code == 200:
    print("OK - Metadata updated")
else:
    print(f"FAILED: {r.status_code} - {r.text}")
    sys.exit(1)

# Step 3: Delete old files
print()
print("=" * 60)
print("Step 3: Delete old files")
print("=" * 60)
r = requests.get(f"{BASE}/deposit/depositions/{new_id}", headers=HEADERS)
dep = r.json()
for f in dep.get("files", []):
    fname = f.get('key') or f.get('filename') or f.get('links', {}).get('self', str(f['id']))
    print(f"  Deleting: {fname}...")
    r = requests.delete(f"{BASE}/deposit/depositions/{new_id}/files/{f['id']}", headers=HEADERS)
    if r.status_code == 204:
        print(f"    OK")
    else:
        print(f"    Failed: {r.status_code}")

# Step 4: Upload fixed files
print()
print("=" * 60)
print("Step 4: Upload fixed files")
print("=" * 60)

# README
readme = """# DeFi Attack Evolution Dataset (824 Cases, 2017-2026)

## Files
- `hacks-verified.csv` — 824 classified DeFi attacks with year, name, category, loss
- `verified-100.csv` — 100 manually verified cases with deep classification

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
MIT — free to use with attribution
"""

print("  Uploading README.md...")
r = requests.put(f"{bucket_url}/README.md", data=readme.encode('utf-8'), headers={"Authorization": f"Bearer {TOKEN}"})
print(f"    {'OK' if r.status_code == 200 else f'Failed: {r.status_code}'}")

# CSV with BOM
csv_path = r"D:\ll\knowledge-base\10-security\zenodo-check\hacks.csv"
with open(csv_path, "rb") as f:
    csv_data = f.read()
if csv_data[:3] != b'\xef\xbb\xbf':
    csv_data = b'\xef\xbb\xbf' + csv_data
    print("  CSV: BOM added")

print("  Uploading hacks-verified.csv...")
r = requests.put(f"{bucket_url}/hacks-verified.csv", data=csv_data, headers={"Authorization": f"Bearer {TOKEN}"})
print(f"    {'OK' if r.status_code == 200 else f'Failed: {r.status_code}'}")

# Verified-100
csv100_path = r"D:\ll\knowledge-base\10-security\zenodo-check\verified-100.csv"
if not os.path.exists(csv100_path):
    urlretrieve("https://zenodo.org/records/21382533/files/verified-100.csv", csv100_path)
with open(csv100_path, "rb") as f:
    csv100_data = f.read()
if csv100_data[:3] != b'\xef\xbb\xbf':
    csv100_data = b'\xef\xbb\xbf' + csv100_data

print("  Uploading verified-100.csv...")
r = requests.put(f"{bucket_url}/verified-100.csv", data=csv100_data, headers={"Authorization": f"Bearer {TOKEN}"})
print(f"    {'OK' if r.status_code == 200 else f'Failed: {r.status_code}'}")

# Step 5: Publish
print()
print("=" * 60)
print("Step 5: Publish new version")
print("=" * 60)
r = requests.post(f"{BASE}/deposit/depositions/{new_id}/actions/publish", headers=HEADERS)
if r.status_code == 202:
    pub = r.json()
    print(f"PUBLISHED!")
    print(f"Version DOI: {pub['doi']}")
    print(f"Concept DOI: https://doi.org/{pub['conceptdoi']}")
    print(f"Page: https://zenodo.org/records/{new_id}")
else:
    print(f"Failed: {r.status_code} - {r.text}")
