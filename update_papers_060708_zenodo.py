# -*- coding: utf-8 -*-
"""Update Papers 06, 07, 08 on Zenodo with Chinese versions and expanded content."""
import json, os, requests

TOKEN = "3dMUkBYgFJRhuDygUbA5CONFZAcYzdxcWAVZgOEwjQMzaliayQZF2vD0uTQc"
BASE = "https://zenodo.org/api"
HEADERS_JSON = {"Authorization": "Bearer %s" % TOKEN, "Content-Type": "application/json"}

PAPERS = [
    {
        "doi": "10.5281/zenodo.21405849",
        "title_en": "A Comprehensive Taxonomy of DeFi Attack Patterns: 50 Vectors from 824 Incidents",
        "desc": "A systematic taxonomy of DeFi attack patterns across 824 incidents (2018-2025). Maps attack vectors to root causes, severity, and financial impact. Now includes comprehensive Chinese translation.",
        "version": "v1.1.0",
        "files": {
            "EN.md": r"D:\ll\knowledge-base\10-security\paper\06-taxonomy\EN.md",
            "EN.pdf": r"D:\ll\knowledge-base\10-security\paper\06-taxonomy\EN.pdf",
            "CN.md": r"D:\ll\knowledge-base\10-security\paper\06-taxonomy\CN.md",
            "CN.pdf": r"D:\ll\knowledge-base\10-security\paper\06-taxonomy\CN.pdf",
        },
    },
    {
        "doi": "10.5281/zenodo.21405916",
        "title_en": "The Hardening Gradient: How DeFi Security Inequality Is Reshaping the Attack Surface",
        "desc": "Analysis of DeFi protocol hardening patterns post-attack. Measures time-to-patch, defense efficacy, and the hardening gradient across protocols. Now includes comprehensive Chinese translation.",
        "version": "v1.1.0",
        "files": {
            "EN.md": r"D:\ll\knowledge-base\10-security\paper\07-hardening-gradient\EN.md",
            "EN.pdf": r"D:\ll\knowledge-base\10-security\paper\07-hardening-gradient\EN.pdf",
            "CN.md": r"D:\ll\knowledge-base\10-security\paper\07-hardening-gradient\CN.md",
            "CN.pdf": r"D:\ll\knowledge-base\10-security\paper\07-hardening-gradient\CN.pdf",
        },
    },
    {
        "doi": "10.5281/zenodo.21405974",
        "title_en": "When Type Hashes Lie: EIP-712 Implementation Errors in DeFi - Evidence from Comprehensive Solidity Code Review",
        "desc": "Large-scale automated validation of 288 EIP-712 implementations reveals 91.7% contain TYPEHASH errors. Identifies three production patterns and the self-consistency trap. Now includes comprehensive Chinese translation and expanded n=288 sample analysis.",
        "version": "v1.1.0",
        "files": {
            "EN.md": r"D:\ll\knowledge-base\10-security\paper\08-eip712-errors\EN.md",
            "EN.pdf": r"D:\ll\knowledge-base\10-security\paper\08-eip712-errors\EN.pdf",
            "CN.md": r"D:\ll\knowledge-base\10-security\paper\08-eip712-errors\CN.md",
            "CN.pdf": r"D:\ll\knowledge-base\10-security\paper\08-eip712-errors\CN.pdf",
        },
    },
]

def upload_file(bucket_url, file_path, filename):
    """Upload a single file to Zenodo bucket."""
    with open(file_path, "rb") as f:
        content = f.read()
    size = len(content)
    r = requests.put(
        "%s/%s" % (bucket_url, filename),
        data=content,
        headers={"Authorization": "Bearer %s" % TOKEN},
    )
    r.raise_for_status()
    return size

for p in PAPERS:
    doi = p["doi"]
    dep_id = doi.split(".")[-1]
    print("")
    print("=" * 60)
    print("Processing: %s" % doi)
    print("  Title: %s" % p["title_en"])
    print("  Deposition ID: %s" % dep_id)

    # Step 1: Create new version
    print("")
    print("[1] Creating new version...")
    r = requests.post(
        "%s/deposit/depositions/%s/actions/newversion" % (BASE, dep_id),
        headers=HEADERS_JSON,
    )
    r.raise_for_status()
    nd = r.json()
    new_id = nd["id"]
    new_doi = nd["metadata"]["prereserve_doi"]["doi"]
    print("  New deposition ID: %s" % new_id)
    print("  Reserved DOI: %s" % new_doi)

    # Step 2: Delete old files
    print("")
    print("[2] Removing old files...")
    existing = nd.get("files", [])
    for f in existing:
        r = requests.delete(
            "%s/deposit/depositions/%s/files/%s" % (BASE, new_id, f["id"]),
            headers={"Authorization": "Bearer %s" % TOKEN},
        )
        print("  Deleted: %s" % f["filename"])

    # Step 3: Upload new files
    print("")
    print("[3] Uploading new files...")
    bucket_url = nd["links"]["bucket"]
    for fname, fpath in p["files"].items():
        if os.path.exists(fpath):
            size = upload_file(bucket_url, fpath, fname)
            print("  Uploaded: %s (%.1f KB)" % (fname, size / 1024.0))
        else:
            print("  SKIP (not found): %s" % fname)

    # Step 4: Update metadata
    print("")
    print("[4] Updating metadata...")
    meta = nd.get("metadata", {})
    meta["title"] = p["title_en"]
    meta["description"] = p["desc"]
    meta["version"] = p["version"]
    meta["publication_date"] = "2026-07-17"

    r = requests.put(
        "%s/deposit/depositions/%s" % (BASE, new_id),
        headers=HEADERS_JSON,
        json={"metadata": meta},
    )
    r.raise_for_status()
    print("  Metadata updated")

    # Step 5: Publish
    print("")
    print("[5] Publishing...")
    r = requests.post(
        "%s/deposit/depositions/%s/actions/publish" % (BASE, new_id),
        headers=HEADERS_JSON,
    )
    r.raise_for_status()
    result = r.json()
    pub_doi = result.get("doi") or result["metadata"]["prereserve_doi"]["doi"]
    print("  Published! DOI: %s" % pub_doi)
    print("  Page: https://zenodo.org/records/%s" % new_id)

print("")
print("=" * 60)
print("All papers updated successfully!")
