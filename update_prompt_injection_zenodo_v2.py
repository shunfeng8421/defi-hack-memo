import os
"""Update Prompt Injection Zenodo record to v2.0.0."""
import json, requests

TOKEN = os.environ.get("ZENODO_TOKEN", "")
BASE = "https://zenodo.org/api"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

print("=== Prompt Injection Paper → v2.0.0 ===\n")

# 0. Find deposition from DOI
print("[0] Looking up existing deposition...")
record_doi = "10.5281/zenodo.21370438"
r = requests.get(f"{BASE}/records/21370438", headers=HEADERS)
if r.status_code == 200:
    rec = r.json()
    dep_id = rec["id"]
    print(f"    Found: deposition {dep_id}, DOI: {rec['doi']}")
else:
    print(f"    Record query failed ({r.status_code}). Trying records list...")
    r = requests.get(f"{BASE}/deposit/depositions", headers=HEADERS, params={"q": "prompt injection mcp"})
    deps = r.json()
    dep_id = None
    for d in deps:
        if "prompt injection" in d.get("title", "").lower():
            dep_id = d["id"]
            print(f"    Found: {dep_id} - {d['title']}")
            break
    if not dep_id:
        print("    NOT FOUND. Listing all depositions...")
        r = requests.get(f"{BASE}/deposit/depositions", headers=HEADERS)
        for d in r.json():
            print(f"    {d['id']}: {d['title'][:80]}")
        raise SystemExit("Cannot find deposition")

# 1. Create new version
print(f"\n[1] Creating new version from deposition {dep_id}...")
r = requests.post(f"{BASE}/deposit/depositions/{dep_id}/actions/newversion", headers=HEADERS)
r.raise_for_status()
nd = r.json()
new_id = nd["id"]
print(f"    New deposition ID: {new_id}")
print(f"    Reserve DOI: {nd['metadata']['prereserve_doi']['doi']}")
bucket = nd["links"]["bucket"]

# 2. Delete old files
print("\n[2] Cleaning old files...")
for f in nd.get("files", []):
    r = requests.delete(f"{BASE}/deposit/depositions/{new_id}/files/{f['id']}", headers=HEADERS)
    print(f"    Deleted: {f['filename']}")

# 3. Upload PDF
print("\n[3] Uploading PDF...")
pdf_path = r"D:\ll\knowledge-base\10-security\paper-prompt-injection-v2.pdf"
with open(pdf_path, "rb") as fh:
    pdf_data = fh.read()
r = requests.put(f"{bucket}/Prompt-Injection-v2.0.pdf", data=pdf_data, headers={"Authorization": f"Bearer {TOKEN}"})
r.raise_for_status()
print(f"    Uploaded: {len(pdf_data)/1024:.1f} KB")

# 4. Metadata
print("\n[4] Updating metadata...")
meta = {
    "title": "Prompt Injection is Not an AI Problem: Why MCP Tool Hardening Matters",
    "creators": [{"name": "Shiqiang Chen", "affiliation": "Independent Researcher"}],
    "description": (
        "Expanded from 3-page experiment report to a 9-page full academic paper. "
        "Includes comprehensive experimental design with 6 injection techniques across 3 defense configurations, "
        "detailed analysis of why prompt filtering fails (structural blindness, semantic ambiguity, language coverage gaps), "
        "practical one-line mitigation strategy (validate_safe_path()), and discussion of attack surface expansion "
        "from prompt injection enabling MCP tool abuse. Connected to companion MCP taxonomy paper (10.5281/zenodo.21383532)."
    ),
    "access_right": "open",
    "license": "mit",
    "upload_type": "publication",
    "publication_type": "preprint",
    "keywords": [
        "prompt injection", "MCP security", "path traversal", "tool hardening",
        "LLM agent security", "CWE-22", "Model Context Protocol"
    ],
    "publication_date": "2026-07-16",
    "version": "v2.0.0",
    "notes": (
        "v2.0.0 expands from a 3-page experiment report to a 9-page paper: full experimental methodology, "
        "6 injection techniques systematically evaluated, defense analysis with configuration comparison, "
        "practical implementation section, and connections to the companion MCP taxonomy paper."
    ),
    "related_identifiers": [
        {
            "relation": "isPreviousVersionOf",
            "identifier": "10.5281/zenodo.21370438",
            "resource_type": "publication-preprint",
            "scheme": "doi"
        },
        {
            "relation": "isSupplementTo",
            "identifier": "10.5281/zenodo.21383532",
            "resource_type": "publication-preprint",
            "scheme": "doi"
        }
    ]
}
r = requests.put(f"{BASE}/deposit/depositions/{new_id}", headers=HEADERS, json={"metadata": meta})
r.raise_for_status()
print("    Metadata updated.")

# 5. Publish
print("\n[5] Publishing...")
r = requests.post(f"{BASE}/deposit/depositions/{new_id}/actions/publish", headers=HEADERS)
r.raise_for_status()
pub = r.json()

print(f"\n=== PUBLISHED ===")
print(f"DOI:    {pub['doi']}")
print(f"URL:    https://doi.org/{pub['doi']}")
print(f"Concept: {pub['conceptdoi']}")
