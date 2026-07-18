import os
"""Update DEFIHACK-824 Zenodo record to v2.0.0 with expanded paper."""
import json, time, requests

TOKEN = os.environ.get("ZENODO_TOKEN", "")
BASE = "https://zenodo.org/api"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

DEPOSITION_ID = "21383211"
NEW_PDF = r"D:\ll\knowledge-base\10-security\paper-deFi-v2.pdf"
CSV_FILE = r"D:\ll\knowledge-base\10-security\zenodo-check\hacks_fixed.csv"

print("=" * 60)
print("Updating DEFIHACK-824 to v2.0.0 (expanded paper)")
print("=" * 60)

# Step 1: Create new version
print("\n1. Creating new version...")
r = requests.post(f"{BASE}/deposit/depositions/{DEPOSITION_ID}/actions/newversion", headers=HEADERS)
r.raise_for_status()
new_dep = r.json()
new_id = new_dep["id"]
bucket_url = new_dep["links"]["bucket"]
new_doi = new_dep["metadata"]["prereserve_doi"]["doi"]
print(f"   New deposition ID: {new_id}")
print(f"   Reserve DOI: {new_doi}")

# Step 2: Delete old files
print("\n2. Removing old files...")
for f in new_dep.get("files", []):
    print(f"   Deleting: {f['filename']}")
    r = requests.delete(f"{BASE}/deposit/depositions/{new_id}/files/{f['id']}", headers=HEADERS)
    try:
        r.raise_for_status()
    except:
        print(f"   (already removed or not deletable)")

# Step 3: Upload new PDF
print("\n3. Uploading expanded paper...")
pdf_filename = "DEFIHACK-824-v2.0.pdf"
with open(NEW_PDF, "rb") as f:
    pdf_data = f.read()
r = requests.put(
    f"{bucket_url}/{pdf_filename}",
    data=pdf_data,
    headers={"Authorization": f"Bearer {TOKEN}"}
)
r.raise_for_status()
print(f"   Uploaded: {pdf_filename} ({len(pdf_data)/1024:.1f} KB)")

# Step 4: Upload CSV dataset
print("\n4. Uploading dataset...")
csv_filename = "defi-hacks-verified-v2.csv"
with open(CSV_FILE, "rb") as f:
    csv_data = f.read()
r = requests.put(
    f"{bucket_url}/{csv_filename}",
    data=csv_data,
    headers={"Authorization": f"Bearer {TOKEN}"}
)
r.raise_for_status()
print(f"   Uploaded: {csv_filename} ({len(csv_data)/1024:.1f} KB)")

# Step 5: Update metadata
print("\n5. Updating metadata...")
metadata = {
    "title": "Evolving Threats, Shifting Patterns: A Multi-Source Verified Dataset and Statistical Analysis of 823 DeFi Security Incidents (2017-2026)",
    "creators": [
        {"name": "Shiqiang Chen", "affiliation": "Independent Researcher"}
    ],
    "description": (
        "Decentralized Finance (DeFi) has suffered over $5 billion in cumulative losses from security incidents, "
        "yet the academic community lacks a large-scale, multi-source-verified dataset to systematically characterize "
        "these threats. We present DEFIHACK-824, a curated dataset of 823 DeFi security incidents spanning 2017 to 2026, "
        "cross-validated against three independent intelligence sources (Rekt News, SlowMist, and CertiK). Each record is "
        "annotated with attack category, confidence level (Gossip/Classified/Ground Truth), and estimated financial loss. "
        "We classify incidents into 14 attack categories and conduct statistical analyses: (1) flash-loan-enabled price "
        "manipulation and reentrancy together account for 51.5% of all attacks; (2) a chi-squared test rejects the null "
        "hypothesis of uniform category distribution at p < 0.0001 (chi-squared = 1,273.2, df = 13); (3) despite "
        "widespread deployment of automated detection tools, the annual attack count has not monotonically decreased. "
        "We further propose a six-layer DeFi threat model and quantify the effectiveness of four defense classes. "
        "The dataset, threat model, and 50 categorized Solidity vulnerability patterns are released under the MIT license."
    ),
    "access_right": "open",
    "license": "cc-by-4.0",
    "upload_type": "publication",
    "publication_type": "preprint",
    "keywords": [
        "DeFi security", "vulnerability dataset", "smart contract audit", "threat modeling",
        "statistical analysis", "flash loan attack", "reentrancy", "cross-validation"
    ],
    "publication_date": "2026-07-16",
    "version": "v2.0.0",
    "notes": (
        "Version 2.0.0 expands the paper from a 1.5-page technical note to a 11-page full academic paper with: "
        "comprehensive introduction, related work (6 papers compared, 5 research gaps), six-layer threat model, "
        "full methodology section with multi-source cross-validation protocol, statistical analysis with chi-squared "
        "and Mann-Kendall tests, defense effectiveness quantification, and a discussion of limitations and future work. "
        "5 of the 50 Solidity vulnerability patterns are included as an appendix with code examples."
    ),
    "related_identifiers": [
        {
            "relation": "isPreviousVersionOf",
            "identifier": "10.5281/zenodo.21383211",
            "resource_type": "publication-preprint",
            "scheme": "doi"
        }
    ]
}

r = requests.put(f"{BASE}/deposit/depositions/{new_id}", headers=HEADERS, json={"metadata": metadata})
r.raise_for_status()
print("   Metadata updated OK")

# Step 6: Publish
print("\n6. Publishing...")
r = requests.post(f"{BASE}/deposit/depositions/{new_id}/actions/publish", headers=HEADERS)
r.raise_for_status()
published = r.json()
final_doi = published["doi"]
concept_doi = published["conceptdoi"]

print("\n" + "=" * 60)
print("PUBLISHED! New version v2.0.0")
print(f"   DOI: {final_doi}")
print(f"   Concept DOI: {concept_doi}")
print(f"   URL: https://doi.org/{final_doi}")
print(f"   Page: https://zenodo.org/records/{new_id}")
print("=" * 60)

print("\nVersion history:")
print(f"   v1.0.0: 10.5281/zenodo.21382533 (original, 1.5 pages, 3 issues)")
print(f"   v1.0.1: 10.5281/zenodo.21383211 (fixed author, DOI, CSV encoding)")
print(f"   v2.0.0: {final_doi} (expanded paper, 11 pages, full academic format)")
