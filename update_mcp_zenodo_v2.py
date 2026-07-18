"""Update MCP Taxonomy Zenodo record to v2.0.0."""
import json, requests

TOKEN = "3dMUkBYgFJRhuDygUbA5CONFZAcYzdxcWAVZgOEwjQMzaliayQZF2vD0uTQc"
BASE = "https://zenodo.org/api"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

print("Updating MCP Taxonomy paper to v2.0.0")

# 1. Create new version
r = requests.post(f"{BASE}/deposit/depositions/21370417/actions/newversion", headers=HEADERS)
r.raise_for_status()
nd = r.json()
print(f"New ID: {nd['id']}")
print(f"Reserve DOI: {nd['metadata']['prereserve_doi']['doi']}")
bucket = nd["links"]["bucket"]

# 2. Delete old files
for f in nd.get("files", []):
    requests.delete(f"{BASE}/deposit/depositions/{nd['id']}/files/{f['id']}", headers=HEADERS)

# 3. Upload PDF
pdf_path = r"D:\ll\knowledge-base\10-security\paper-mcp-taxonomy-v2.pdf"
with open(pdf_path, "rb") as fh:
    pdf_data = fh.read()
r = requests.put(f"{bucket}/MCP-Security-Taxonomy-v2.0.pdf", data=pdf_data, headers={"Authorization": f"Bearer {TOKEN}"})
r.raise_for_status()
print(f"Uploaded PDF ({len(pdf_data)/1024:.1f} KB)")

# 4. Metadata
meta = {
    "title": "An Empirical Study of Model Context Protocol (MCP) Server Security: Taxonomy, Large-Scale Scanning, and Defense Framework",
    "creators": [{"name": "Shiqiang Chen", "affiliation": "Independent Researcher"}],
    "description": (
        "Expanded to a 10-page full academic paper. Six attack surfaces, large-scale scan of 620 MCP packages "
        "using 46 custom Semgrep rules, five-level defense maturity framework, and 91-node MCP security knowledge graph. "
        "Includes 2 original CVEs (CVE-2025-49596, CVE-2026-23744)."
    ),
    "access_right": "open",
    "license": "mit",
    "upload_type": "publication",
    "publication_type": "preprint",
    "keywords": ["Model Context Protocol", "MCP security", "LLM agent security", "vulnerability taxonomy", "Semgrep", "CVE"],
    "publication_date": "2026-07-16",
    "version": "v2.0.0",
    "notes": (
        "v2.0.0 expands from a 5-page taxonomy to a 10-page paper: ecosystem scan methodology (620 packages), "
        "46 Semgrep rules, 91-node knowledge graph, defense coverage quantification, CVE case studies."
    ),
    "related_identifiers": [{
        "relation": "isPreviousVersionOf",
        "identifier": "10.5281/zenodo.21370417",
        "resource_type": "publication-preprint",
        "scheme": "doi"
    }]
}
r = requests.put(f"{BASE}/deposit/depositions/{nd['id']}", headers=HEADERS, json={"metadata": meta})
r.raise_for_status()

# 5. Publish
r = requests.post(f"{BASE}/deposit/depositions/{nd['id']}/actions/publish", headers=HEADERS)
r.raise_for_status()
pub = r.json()

print(f"\nPUBLISHED!")
print(f"DOI: {pub['doi']}")
print(f"URL: https://doi.org/{pub['doi']}")
print(f"Concept DOI: {pub['conceptdoi']}")
