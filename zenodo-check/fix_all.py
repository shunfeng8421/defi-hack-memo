"""Fix all 3 issues on DeFi Attack Dataset (10.5281/zenodo.21382533)."""
import json, os, sys, requests
from urllib.request import urlretrieve

sys.stdout.reconfigure(encoding='utf-8')

TOKEN = "3dMUkBYgFJRhuDygUbA5CONFZAcYzdxcWAVZgOEwjQMzaliayQZF2vD0uTQc"
BASE = "https://zenodo.org/api"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
DEP_ID = "21382533"

print("=" * 60)
print("FIX 1: Update author name (shunfeng8421 -> Shiqiang Chen)")
print("=" * 60)

r = requests.put(
    f"{BASE}/deposit/depositions/{DEP_ID}",
    headers=HEADERS,
    json={
        "metadata": {
            "creators": [{"name": "Shiqiang Chen", "affiliation": "Independent Researcher"}],
            "title": "DeFi Attack Evolution Dataset (824 Cases, 2017-2026)",
            "description": "A comprehensive dataset of 824 DeFi security incidents from 2017 to 2026. Each record includes year, project name, attack category, loss amount, and chain. 50 cases are ground-truth verified by 2+ independent sources (Rekt News, SlowMist, CertiK). Categories span flash loan attacks, reentrancy, permission bugs, price manipulation, bridge exploits, governance attacks, and more. Suitable for ML training, trend analysis, and security research.",
            "access_right": "open",
            "license": "mit-license",
            "upload_type": "dataset",
            "keywords": [
                "DeFi security",
                "smart contract audit",
                "blockchain attacks",
                "crypto hacks",
                "Web3 security",
                "flash loan",
                "reentrancy",
                "MEV"
            ],
            "notes": "Version 1.0. Dataset compiled from DeFiHackLabs PoC reproductions and cross-validated with Rekt News, SlowMist Hacked Archive, and CertiK alerts. Ground-truth labels confirmed by 2+ independent sources."
        }
    }
)

if r.status_code == 200:
    print("OK - Author name updated to Shiqiang Chen")
else:
    print(f"FAILED: {r.status_code}")
    print(r.text)
    sys.exit(1)

print()
print("=" * 60)
print("FIX 2: Create new version for updated README and CSV")
print("=" * 60)

r = requests.post(
    f"{BASE}/deposit/depositions/{DEP_ID}/actions/newversion",
    headers=HEADERS
)

if r.status_code == 201:
    new_dep = r.json()
    new_id = new_dep["id"]
    bucket_url = new_dep["links"]["bucket"]
    print(f"New version draft: {new_id}")
    print(f"Bucket: {bucket_url}")
else:
    print(f"FAILED: {r.status_code}")
    print(r.text)
    sys.exit(1)

print()
print("=" * 60)
print("FIX 3: Delete old files and upload fixed ones")
print("=" * 60)

# Delete old files
for f in new_dep.get("files", []):
    print(f"  Deleting: {f['key']}...")
    r = requests.delete(
        f"{BASE}/deposit/depositions/{new_id}/files/{f['id']}",
        headers=HEADERS
    )
    if r.status_code == 204:
        print(f"    Deleted OK")
    else:
        print(f"    Delete failed: {r.status_code}")

print()

# Build fixed README
readme = """# DeFi Attack Evolution Dataset (824 Cases, 2017-2026)

## Files
- `hacks-verified.csv` — 824 classified DeFi attacks with year, name, category, loss
- `verified-100.csv` — 100 manually verified cases with deep classification

## Metadata
- Source: DeFiHackLabs PoC reproductions
- Cross-validated: Rekt News, SlowMist, CertiK
- Ground-truth labels: 50 cases confirmed by 2+ independent sources
- Classification: 14 categories (keyword-based + manual verification)

## Citation
If you use this dataset, please cite:
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

# Upload fixed README
print("Uploading fixed README...")
r = requests.put(
    f"{bucket_url}/README.md",
    data=readme.encode('utf-8'),
    headers={"Authorization": f"Bearer {TOKEN}"}
)
if r.status_code == 200:
    print("  README uploaded OK")
else:
    print(f"  README upload failed: {r.status_code}")

# Fix CSV: add UTF-8 BOM
print()
print("Fixing CSV with UTF-8 BOM...")
csv_path = r"D:\ll\knowledge-base\10-security\zenodo-check\hacks.csv"
with open(csv_path, "rb") as f:
    csv_data = f.read()

# Add BOM if not present
if csv_data[:3] != b'\xef\xbb\xbf':
    csv_data = b'\xef\xbb\xbf' + csv_data
    print(f"  BOM added, size: {len(csv_data)} bytes")

print("Uploading fixed CSV...")
r = requests.put(
    f"{bucket_url}/hacks-verified.csv",
    data=csv_data,
    headers={"Authorization": f"Bearer {TOKEN}"}
)
if r.status_code == 200:
    print("  CSV uploaded OK")
else:
    print(f"  CSV upload failed: {r.status_code}")

# Also fix verified-100.csv
print()
csv100_path = r"D:\ll\knowledge-base\10-security\zenodo-check\verified-100.csv"
if not os.path.exists(csv100_path):
    # Download it
    urlretrieve(
        "https://zenodo.org/records/21382533/files/verified-100.csv",
        csv100_path
    )

with open(csv100_path, "rb") as f:
    csv100_data = f.read()

if csv100_data[:3] != b'\xef\xbb\xbf':
    csv100_data = b'\xef\xbb\xbf' + csv100_data

print("Uploading fixed verified-100.csv...")
r = requests.put(
    f"{bucket_url}/verified-100.csv",
    data=csv100_data,
    headers={"Authorization": f"Bearer {TOKEN}"}
)
if r.status_code == 200:
    print("  verified-100.csv uploaded OK")
else:
    print(f"  verified-100.csv upload failed: {r.status_code}")

print()
print("=" * 60)
print("FIX 4: Publish new version")
print("=" * 60)

r = requests.post(
    f"{BASE}/deposit/depositions/{new_id}/actions/publish",
    headers=HEADERS
)

if r.status_code == 202:
    published = r.json()
    print(f"PUBLISHED!")
    print(f"New version DOI: {published['doi']}")
    print(f"Concept DOI (always latest): https://doi.org/{published['conceptdoi']}")
    print(f"Zenodo page: https://zenodo.org/records/{new_id}")
else:
    print(f"Publish failed: {r.status_code}")
    print(r.text)
