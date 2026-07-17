#!/usr/bin/env python3
"""
EIP-712 TYPEHASH Verifier v6 - Simplified Search + Robust Analysis
Uses single-word searches to avoid gh search code strict matching.
"""
import re, json, base64, subprocess, time, sys, hashlib
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = Path(__file__).parent / "eip712_final"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ===========================================================
# Source fetching
# ===========================================================
def gh_fetch(repo: str, path: str, ref: str = None) -> str:
    url = f"repos/{repo}/contents/{path}"
    if ref:
        url += f"?ref={ref}"
    for attempt in range(3):
        try:
            r = subprocess.run(['gh', 'api', url, '--jq', '.content'],
                             capture_output=True, text=True, timeout=30)
            if r.returncode == 0 and r.stdout.strip():
                content_b64 = r.stdout.replace('\n', '').replace('\r', '').strip()
                try:
                    return base64.b64decode(content_b64).decode('utf-8', errors='replace')
                except:
                    return None
            time.sleep(1.5)
        except:
            time.sleep(1.5)
    return None


def gh_search(query: str, limit: int = 50) -> list:
    """Search using single-word or simple phrase."""
    cmd = ['gh', 'search', 'code', query, 'language:Solidity',
           '--limit', str(limit), '--json', 'url,repository,path']
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if r.returncode == 0 and r.stdout.strip():
            data = json.loads(r.stdout)
            results = []
            for item in data:
                repo = item['repository']['nameWithOwner']
                path = item['path']
                url = item.get('url', '')
                ref_match = re.search(r'/blob/([^/]+)/', url)
                ref = ref_match.group(1) if ref_match else None
                results.append((repo, path, ref))
            return results
    except Exception as e:
        pass
    return []


# ===========================================================
# Parsing
# ===========================================================
def extract_typehash_entries(source: str) -> list:
    results = []
    
    # keccak256("...") pattern
    p1 = r"""bytes32\s+(?:public\s+)?(?:private\s+)?(?:internal\s+)?(?:constant\s+)?
            (\w*(?:_?TYPE_?HASH|TYPEHASH)\w*)\s*=\s*keccak256\s*\(\s*
            (?:abi\.encodePacked\s*\(\s*)?(?:bytes\s*\()?\s*
            ["']((?:[^"\\]|\\.)*)["']"""
    
    for m in re.finditer(p1, source, re.IGNORECASE | re.VERBOSE):
        name = m.group(1)
        sig = m.group(2)
        line = source[:m.start()].count('\n') + 1
        results.append({'name': name, 'string_value': sig, 'line_no': line, 'is_hex': False})
    
    # hex constant 0x... pattern
    p2 = r"""bytes32\s+(?:public\s+)?(?:private\s+)?(?:internal\s+)?(?:constant\s+)?
            (\w*(?:_?TYPE_?HASH|TYPEHASH)\w*)\s*=\s*(0x[a-fA-F0-9]{64})"""
    
    for m in re.finditer(p2, source, re.IGNORECASE | re.VERBOSE):
        name = m.group(1)
        hex_val = m.group(2)
        if not any(r['name'] == name for r in results):
            line = source[:m.start()].count('\n') + 1
            results.append({'name': name, 'string_value': hex_val, 'line_no': line, 'is_hex': True})
    
    return results


def extract_functions(source: str) -> dict:
    funcs = {}
    pattern = r'function\s+(\w+)\s*\(([^)]*)\)'
    
    for m in re.finditer(pattern, source):
        name = m.group(1)
        params_str = m.group(2).strip()
        line = source[:m.start()].count('\n') + 1
        
        params = []
        if params_str:
            for param in params_str.split(','):
                param = param.strip()
                parts = param.split()
                if len(parts) >= 2:
                    actual_parts = [p for p in parts if p not in ('memory', 'calldata', 'storage')]
                    if len(actual_parts) >= 2:
                        params.append({'name': actual_parts[-1], 'type': actual_parts[0]})
        
        if name not in funcs:
            funcs[name] = []
        funcs[name].append({'name': name, 'params': params, 'line_no': line})
    
    return funcs


# ===========================================================
# Validation
# ===========================================================
def parse_signature(sig: str):
    m = re.match(r'(\w+)\s*\(([^)]*)\)', sig.strip())
    if not m:
        return None, None
    func_name = m.group(1)
    params_str = m.group(2).strip()
    param_types = []
    if params_str:
        for p in params_str.split(','):
            p = p.strip()
            parts = p.split()
            if parts:
                param_types.append(parts[0])
    return func_name, param_types


def canonical_type(t: str) -> str:
    t = t.strip()
    if t.endswith('[]'):
        return canonical_type(t[:-2]) + '[]'
    aliases = {'uint': 'uint256', 'int': 'int256'}
    t_lower = t.lower()
    if t_lower in aliases:
        return aliases[t_lower]
    misspellings = {
        'addres': 'address', 'adress': 'address',
        'boool': 'bool', 'uint2566': 'uint256',
        'bytess32': 'bytes32', 'stringg': 'string',
    }
    if t_lower in misspellings:
        return misspellings[t_lower]
    return t


def verify_typehash(th_entry, functions):
    sig = th_entry['string_value']
    
    if th_entry.get('is_hex'):
        return {'is_valid': None, 'errors': [{'type': 'HEX_CONSTANT', 'details': 'Pre-computed hex; need original signature'}]}
    
    func_name, th_params = parse_signature(sig)
    
    if func_name is None:
        return {'is_valid': False, 'errors': [{'type': 'PARSE_ERROR', 'details': f'Cannot parse: "{sig}"'}]}
    
    if func_name not in functions:
        return {'is_valid': None, 'errors': [{'type': 'FUNC_ELSEWHERE', 'details': f'"{func_name}" not in this file (parent contract?)'}]}
    
    func_variants = functions[func_name]
    best_match = None
    best_errors = None
    
    for func in func_variants:
        errors = []
        ap = func['params']
        
        if len(th_params) != len(ap):
            errors.append({'type': 'PARAM_COUNT', 'details': f'TYPEHASH={len(th_params)} params, Func={len(ap)} params'})
        
        for i in range(min(len(th_params), len(ap))):
            tt = canonical_type(th_params[i])
            at = canonical_type(ap[i]['type'])
            if tt.lower() != at.lower():
                errors.append({'type': 'TYPE_MISMATCH', 'details': f'Param {i+1}: "{th_params[i]}" vs "{ap[i]["type"]}"'})
        
        if len(errors) == 0:
            best_match, best_errors = func, []
            break
        if best_errors is None or len(errors) < len(best_errors):
            best_match, best_errors = func, errors
    
    # Determine if the NAME of the param is the issue vs actual type
    # (sometimes signature has different param names but same types - that's OK)
    has_only_name_diff = all(e['type'] == 'PARAM_COUNT' for e in best_errors) if best_errors else False
    
    return {
        'is_valid': len(best_errors) == 0,
        'errors': best_errors,
        'func_name': func_name,
        'func_params': best_match['params'] if best_match else [],
        'th_params': th_params,
    }


# ===========================================================
# Main
# ===========================================================
def main():
    print("=" * 70)
    print("EIP-712 TYPEHASH Verifier v6")
    print("=" * 70)
    
    # Step 1: Search with simplified queries
    print("\n[Step 1] Searching GitHub for TYPEHASH identifiers...")
    
    # These are single identifiers - gh search code handles them well
    search_queries = [
        "PERMIT_TYPEHASH",
        "DOMAIN_TYPEHASH",  
        "CLAIM_TYPEHASH",
        "MINT_TYPEHASH",
        "TRANSFER_TYPEHASH",
        "_TYPEHASH",
        "DELEGATION_TYPEHASH",
        "ORDER_TYPEHASH",
        "BID_TYPEHASH",
        "SWAP_TYPEHASH",
        "VOTE_TYPEHASH",
        "BURN_TYPEHASH",
    ]
    
    all_files = {}
    for query in search_queries:
        results = gh_search(query, limit=20)
        for repo, path, ref in results:
            key = (repo, path)
            if key not in all_files:
                all_files[key] = ref
        print(f"  {query}: {len(results)} results (total unique: {len(all_files)})")
        time.sleep(1.5)
    
    print(f"\n  Total unique files: {len(all_files)}")
    
    if not all_files:
        print("ERROR: No files found. Aborting.")
        return
    
    # Step 2: Fetch sources
    print(f"\n[Step 2] Fetching {len(all_files)} source files...")
    
    sources = {}
    for i, ((repo, path), ref) in enumerate(all_files.items()):
        source = gh_fetch(repo, path, ref)
        if source:
            sources[(repo, path)] = source
        if (i + 1) % 30 == 0:
            print(f"  Fetched: {len(sources)}/{i+1}")
        time.sleep(0.25)
    
    print(f"  Fetched: {len(sources)}/{len(all_files)}")
    
    # Save
    serializable = {f"{r}/{p}": s for (r, p), s in sources.items()}
    with open(OUTPUT_DIR / 'sources.json', 'w', encoding='utf-8') as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)
    
    # Step 3: Verify
    print(f"\n[Step 3] Verifying...")
    
    all_findings = []
    
    for (repo, path), source in sources.items():
        th_entries = extract_typehash_entries(source)
        functions = extract_functions(source)
        
        for th in th_entries:
            validation = verify_typehash(th, functions)
            all_findings.append({
                'repo': repo,
                'path': path,
                'typehash_name': th['name'],
                'typehash_value': th['string_value'],
                'line_no': th['line_no'],
                'is_hex': th.get('is_hex', False),
                'validation': validation,
            })
    
    # Step 4: Stats
    total = len(all_findings)
    valid = sum(1 for f in all_findings if f['validation']['is_valid'] is True)
    invalid = sum(1 for f in all_findings if f['validation']['is_valid'] is False)
    undetermined = sum(1 for f in all_findings if f['validation']['is_valid'] is None)
    determinable = valid + invalid
    
    if determinable == 0:
        print("\nNothing determinable from sampled contracts. They likely all use pre-computed hex or inherited TYPEHASH.")
        print("This itself is a finding: production EIP-712 contracts overwhelmingly use pre-computed hashes.")
        return
    
    error_rate = (invalid / determinable * 100)
    
    # Error categorization
    error_cat = defaultdict(int)
    for f in all_findings:
        if f['validation']['is_valid'] is False:
            for err in f['validation']['errors']:
                error_cat[err['type']] += 1
    
    # Report
    report = f"""
{'='*70}
EIP-712 TYPEHASH ECOSYSTEM VALIDATION REPORT
{'='*70}

SAMPLING:
  Files fetched:              {len(sources)}
  TYPEHASH entries analyzed:  {total}

RESULTS:
  Valid:           {valid} ({valid/determinable*100:.1f}% of determinable)
  Invalid:         {invalid} ({error_rate:.1f}%)
  Undetermined:    {undetermined}

** ERROR RATE: {error_rate:.1f}% (n={determinable} determinable entries) **

ERROR CATEGORIES:
"""
    
    for cat, count in sorted(error_cat.items(), key=lambda x: -x[1]):
        report += f"  [{cat}]: {count}\n"
    
    report += f"\n{'='*70}\nINVALID DETAILS:\n{'='*70}\n"
    
    for f in all_findings:
        if f['validation']['is_valid'] is False:
            report += f"\n[ERR] {f['repo']}/{f['path']} (L{f['line_no']})\n  {f['typehash_value']}\n"
            for err in f['validation']['errors']:
                report += f"  -> {err['details']}\n"
    
    report += f"\n{'='*70}\nVALID SAMPLE:\n{'='*70}\n"
    
    for f in all_findings:
        if f['validation']['is_valid'] is True:
            report += f"[OK] {f['repo']}: {f['typehash_value']}\n"
    
    # Save
    report_path = OUTPUT_DIR / 'FINAL_REPORT.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    findings_path = OUTPUT_DIR / 'all_findings.json'
    with open(findings_path, 'w', encoding='utf-8') as f:
        json.dump(all_findings, f, indent=2, ensure_ascii=False)
    
    try:
        print(report)
    except:
        print(report.encode('ascii', errors='replace').decode('ascii'))
    
    print(f"\nReport: {report_path}")
    print(f"Findings: {findings_path}")
    
    return all_findings


if __name__ == '__main__':
    main()
