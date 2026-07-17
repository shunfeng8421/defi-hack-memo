#!/usr/bin/env python3
"""
EIP-712 TYPEHASH Validator: Large-Scale Sampling Tool
Scans GitHub for EIP-712 implementations, extracts TYPEHASH constants,
validates them against actual function signatures, and reports error rates.

Usage: python eip712_sample.py
"""

import re
import json
import hashlib
import subprocess
import time
import os
import sys
from pathlib import Path
from collections import defaultdict

# ============================================================
# Configuration
# ============================================================
OUTPUT_DIR = Path(__file__).parent / "eip712_samples"
RESULTS_FILE = OUTPUT_DIR / "results.json"
REPOS_FILE = OUTPUT_DIR / "repos.json"

# Known solidity type canonical names (lowercased for comparison)
SOLIDITY_TYPES = {
    'address', 'bool', 'string', 'bytes', 'bytes1', 'bytes2', 'bytes3',
    'bytes4', 'bytes5', 'bytes6', 'bytes7', 'bytes8', 'bytes9', 'bytes10',
    'bytes11', 'bytes12', 'bytes13', 'bytes14', 'bytes15', 'bytes16',
    'bytes17', 'bytes18', 'bytes19', 'bytes20', 'bytes21', 'bytes22',
    'bytes23', 'bytes24', 'bytes25', 'bytes26', 'bytes27', 'bytes28',
    'bytes29', 'bytes30', 'bytes31', 'bytes32',
    'uint8', 'uint16', 'uint24', 'uint32', 'uint40', 'uint48', 'uint56',
    'uint64', 'uint72', 'uint80', 'uint88', 'uint96', 'uint104', 'uint112',
    'uint120', 'uint128', 'uint136', 'uint144', 'uint152', 'uint160',
    'uint168', 'uint176', 'uint184', 'uint192', 'uint200', 'uint208',
    'uint216', 'uint224', 'uint232', 'uint240', 'uint248', 'uint256',
    'int8', 'int16', 'int24', 'int32', 'int40', 'int48', 'int56',
    'int64', 'int72', 'int80', 'int88', 'int96', 'int104', 'int112',
    'int120', 'int128', 'int136', 'int144', 'int152', 'int160',
    'int168', 'int176', 'int184', 'int192', 'int200', 'int208',
    'int216', 'int224', 'int232', 'int240', 'int248', 'int256',
}

# Known misspellings → correct forms
KNOWN_MISSPELLINGS = {
    'addres': 'address',
    'adress': 'address',
    'adddress': 'address',
    'adrress': 'address',
    'recipent': 'recipient',  # not a type but common
    'uint2566': 'uint256',
    'uint256256': 'uint256',
    'bool': 'bool',  # correct
    'boool': 'bool',
    'bytes32': 'bytes32',
    'bytess32': 'bytes32',
    'stringg': 'string',
    'strng': 'string',
}

# ============================================================
# Solidity Parser (simplified)
# ============================================================

def extract_typehash_constants(source: str) -> list[dict]:
    """
    Extract all TYPEHASH constant definitions from Solidity source.
    Returns list of {name, typehash_string, line_no}
    """
    results = []
    
    # Pattern: bytes32 [constant] [public] NAME = keccak256(...);
    # or: bytes32 [constant] [public] NAME = 0x...;
    patterns = [
        # keccak256(bytes("..."))  or  keccak256("...")
        r'(?:bytes32)\s+(?:constant\s+)?(?:public\s+)?(\w*(?:TYPE_?HASH|TYPEHASH)\w*)\s*=\s*keccak256\(\s*(?:bytes\()?["\']((?:[^"\\]|\\.)*)["\']\s*\)?\s*\)',
        # sha256("...")
        r'(?:bytes32)\s+(?:constant\s+)?(?:public\s+)?(\w*(?:TYPE_?HASH|TYPEHASH)\w*)\s*=\s*sha256\(\s*(?:bytes\()?["\']((?:[^"\\]|\\.)*)["\']\s*\)?\s*\)',
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, source, re.IGNORECASE | re.DOTALL):
            name = match.group(1)
            typehash_str = match.group(2)
            line_no = source[:match.start()].count('\n') + 1
            results.append({
                'name': name,
                'typehash_str': typehash_str,
                'line_no': line_no,
            })
    
    return results


def extract_function_for_typehash(source: str, typehash_name: str) -> list[dict]:
    """
    Try to find the function that uses a given TYPEHASH.
    Returns list of {name, params: [{name, type}], line_no}
    """
    results = []
    
    # Find where TYPEHASH is used in abi.encode
    # Pattern: abi.encode(TYPEHASH_NAME, param1, param2, ...)
    usage_pattern = rf'abi\.encode\s*\(\s*{re.escape(typehash_name)}\s*,([^)]+)\)'
    
    funcs_seen = set()
    
    for match in re.finditer(usage_pattern, source):
        params_str = match.group(1).strip()
        # Find the enclosing function
        # Search backward for "function ...("
        before = source[:match.start()]
        # Find the last function declaration before this usage
        func_match = None
        for fm in re.finditer(r'function\s+(\w+)\s*\(([^)]*)\)', before):
            func_match = fm
        
        if func_match:
            func_name = func_match.group(1)
            func_params_str = func_match.group(2)
            
            func_key = f"{func_name}({func_params_str})"
            if func_key in funcs_seen:
                continue
            funcs_seen.add(func_key)
            
            params = []
            if func_params_str.strip():
                for param in func_params_str.split(','):
                    param = param.strip()
                    parts = param.split()
                    if len(parts) >= 2:
                        # Type may include 'memory', 'calldata', 'storage'
                        param_type = parts[0]
                        param_name = parts[-1]
                        # Remove 'memory', 'calldata', 'storage' keywords
                        if len(parts) >= 3 and parts[1] in ('memory', 'calldata', 'storage', 'indexed'):
                            param_type = parts[0]
                        params.append({
                            'name': param_name,
                            'type': param_type,
                        })
            
            results.append({
                'name': func_name,
                'params': params,
                'line_no': before.count('\n') + 1,
            })
    
    return results


def parse_typehash_string(typehash_str: str) -> tuple[str, list[str]]:
    """
    Parse a TYPEHASH string like "claimTokens(address recipient, uint256 amount)"
    into (function_name, [param_types]).
    """
    # Remove whitespace
    cleaned = typehash_str.strip()
    
    # Match: FunctionName(type1 p1, type2 p2, ...)
    match = re.match(r'(\w+)\s*\(([^)]*)\)', cleaned)
    if not match:
        return None, None
    
    func_name = match.group(1)
    params_str = match.group(2).strip()
    
    param_types = []
    if params_str:
        for param in params_str.split(','):
            param = param.strip()
            # Extract type (first word)
            parts = param.split()
            if parts:
                param_types.append(parts[0])
    
    return func_name, param_types


def canonicalize_type(t: str) -> str:
    """Return canonical form of a Solidity type string."""
    t = t.strip()
    # Check for arrays
    is_array = t.endswith('[]')
    base = t[:-2] if is_array else t
    
    # Check misspellings
    base_lower = base.lower()
    if base_lower in KNOWN_MISSPELLINGS:
        base = KNOWN_MISSPELLINGS[base_lower]
    
    # Reconstruct
    if is_array:
        return base + '[]'
    return base


def validate_typehash(typehash_str: str, func_params: list[dict]) -> dict:
    """
    Validate that a TYPEHASH string matches the actual function parameters.
    Returns {is_valid, errors: [{type, details}]}
    """
    errors = []
    
    func_name, typehash_params = parse_typehash_string(typehash_str)
    
    if func_name is None:
        return {'is_valid': False, 'errors': [{'type': 'PARSE_ERROR', 'details': 'Cannot parse TYPEHASH string'}]}
    
    # Check function name match
    if func_params:
        actual_func_name = func_params[0]['name']
        if func_name != actual_func_name:
            errors.append({
                'type': 'FUNC_NAME_MISMATCH',
                'details': f"TYPEHASH says '{func_name}' but function is '{actual_func_name}'"
            })
    
    # Check parameter count
    actual_params = func_params[0]['params'] if func_params else []
    
    if len(typehash_params) != len(actual_params):
        errors.append({
            'type': 'PARAM_COUNT_MISMATCH',
            'details': f"TYPEHASH has {len(typehash_params)} params, function has {len(actual_params)}"
        })
    
    # Check parameter types (up to min length)
    check_count = min(len(typehash_params), len(actual_params))
    for i in range(check_count):
        th_type = canonicalize_type(typehash_params[i])
        actual_type = canonicalize_type(actual_params[i])
        
        if th_type.lower() != actual_type.lower():
            # Check if it's a known misspelling
            if th_type.lower() in KNOWN_MISSPELLINGS:
                errors.append({
                    'type': 'TYPE_1_SPELLING',
                    'details': f"Param {i+1}: TYPEHASH has '{typehash_params[i]}' (misspelled), function has '{actual_params[i]['type']}'"
                })
            else:
                errors.append({
                    'type': 'TYPE_2_MISMATCH',
                    'details': f"Param {i+1}: TYPEHASH has '{typehash_params[i]}', function has '{actual_params[i]['type']}'"
                })
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'typehash_params': typehash_params,
        'actual_params': [p['type'] for p in actual_params],
    }


# ============================================================
# GitHub Search via API
# ============================================================

def search_github_repos(query: str, max_pages: int = 10) -> list[dict]:
    """
    Search GitHub code for Solidity files containing TYPEHASH patterns.
    Uses the GitHub Search API (no auth needed for public repos, but rate-limited).
    """
    all_items = []
    
    # Search queries
    queries = [
        'TYPEHASH language:Solidity',
        '_TYPE_HASH language:Solidity',
        'TYPE_HASH keccak256 language:Solidity',
    ]
    
    for q in queries:
        for page in range(1, max_pages + 1):
            url = f"https://api.github.com/search/code?q={q.replace(' ', '+')}&per_page=30&page={page}"
            print(f"  Searching: {url[:100]}...")
            
            cmd = ['curl', '-s', '-H', 'Accept: application/vnd.github.v3+json', url]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    print(f"    curl failed: {result.stderr[:200]}")
                    break
                
                data = json.loads(result.stdout)
                
                if 'items' not in data:
                    if 'message' in data:
                        print(f"    API message: {data['message']}")
                    break
                
                items = data['items']
                if not items:
                    break
                
                for item in items:
                    all_items.append({
                        'repo': item['repository']['full_name'],
                        'path': item['path'],
                        'url': item['html_url'],
                        'raw_url': f"https://raw.githubusercontent.com/{item['repository']['full_name']}/master/{item['path']}",
                    })
                
                print(f"    Found {len(items)} items (total: {len(all_items)})")
                time.sleep(2)  # Rate limiting
                
            except json.JSONDecodeError:
                print(f"    JSON decode error: {result.stdout[:200]}")
                break
            except Exception as e:
                print(f"    Error: {e}")
                break
        
        time.sleep(5)  # Between queries
    
    return all_items


def search_github_repos_v2(max_per_query: int = 100) -> list[dict]:
    """
    Alternative approach: search using multiple specific queries for better coverage.
    Includes: top DeFi protocols, known EIP-712 users, and random sampling.
    """
    all_items = []
    
    # Phase 1: Search for common TYPEHASH patterns
    search_queries = [
        'bytes32 constant TYPEHASH language:Solidity',
        'bytes32 public constant TYPEHASH language:Solidity',
        'bytes32 private constant TYPEHASH language:Solidity',
        'bytes32 internal constant TYPEHASH language:Solidity',
        'bytes32 immutable TYPEHASH language:Solidity',
    ]
    
    for q in search_queries:
        url = f"https://api.github.com/search/code?q={q.replace(' ', '+')}&per_page={max_per_query}"
        print(f"  Searching: {q[:80]}...")
        
        cmd = ['curl', '-s', '-H', 'Accept: application/vnd.github.v3+json', url]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            data = json.loads(result.stdout)
            
            if 'items' in data:
                for item in data['items']:
                    all_items.append({
                        'repo': item['repository']['full_name'],
                        'path': item['path'],
                        'url': item['html_url'],
                    })
                print(f"    Got {len(data['items'])} results (total: {len(all_items)})")
            else:
                print(f"    API response: {data.get('message', 'unknown')[:100]}")
        except Exception as e:
            print(f"    Error: {e}")
        
        time.sleep(3)
    
    # Phase 2: Search by known EIP-712 function patterns
    func_queries = [
        'PERMIT_TYPEHASH language:Solidity',
        'CLAIM_TYPEHASH language:Solidity',
        'VOTE_TYPEHASH language:Solidity',
        'TRANSFER_TYPEHASH language:Solidity',
        'MINT_TYPEHASH language:Solidity',
        '_hashTypedDataV4 language:Solidity',
        'EIP712 language:Solidity keccak256',
    ]
    
    for q in func_queries:
        url = f"https://api.github.com/search/code?q={q.replace(' ', '+')}&per_page=50"
        print(f"  Searching: {q[:80]}...")
        
        cmd = ['curl', '-s', '-H', 'Accept: application/vnd.github.v3+json', url]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            data = json.loads(result.stdout)
            
            if 'items' in data:
                for item in data['items']:
                    all_items.append({
                        'repo': item['repository']['full_name'],
                        'path': item['path'],
                        'url': item['html_url'],
                    })
                print(f"    Got {len(data['items'])} results (total: {len(all_items)})")
        except Exception as e:
            print(f"    Error: {e}")
        
        time.sleep(3)
    
    # Deduplicate by repo+path
    seen = set()
    unique = []
    for item in all_items:
        key = f"{item['repo']}/{item['path']}"
        if key not in seen:
            seen.add(key)
            unique.append(item)
    
    print(f"\n  Total unique repos: {len(unique)}")
    return unique


def download_file(raw_url: str, output_path: Path) -> bool:
    """Download a single file from GitHub raw."""
    cmd = ['curl', '-sL', '--max-time', '15', '-o', str(output_path), raw_url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0
    except Exception:
        return False


# ============================================================
# Analysis Engine
# ============================================================

def analyze_file(filepath: Path) -> dict:
    """
    Analyze a Solidity file for TYPEHASH errors.
    Returns {file, typehash_count, errors: [...], findings: [...]}
    """
    try:
        source = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        return {'file': str(filepath), 'error': str(e)}
    
    # Extract TYPEHASH constants
    typehashes = extract_typehash_constants(source)
    
    if not typehashes:
        return {'file': str(filepath), 'typehash_count': 0, 'findings': []}
    
    findings = []
    for th in typehashes:
        # Find associated functions
        functions = extract_function_for_typehash(source, th['name'])
        
        # Validate
        if functions:
            validation = validate_typehash(th['typehash_str'], functions)
        else:
            validation = {
                'is_valid': None,  # cannot determine
                'errors': [{'type': 'NO_FUNC_FOUND', 'details': 'Could not find function using this TYPEHASH'}]
            }
        
        findings.append({
            'typehash_name': th['name'],
            'typehash_str': th['typehash_str'],
            'typehash_line': th['line_no'],
            'associated_function': functions[0]['name'] if functions else None,
            'func_params': functions[0]['params'] if functions else [],
            'func_line': functions[0]['line_no'] if functions else None,
            'validation': validation,
        })
    
    return {
        'file': str(filepath),
        'typehash_count': len(typehashes),
        'findings': findings,
    }


# ============================================================
# Report Generation
# ============================================================

def generate_report(all_results: list[dict]) -> str:
    """Generate a summary report from all analysis results."""
    
    total_files = len(all_results)
    files_with_typehash = [r for r in all_results if r.get('typehash_count', 0) > 0]
    total_typehashes = sum(r.get('typehash_count', 0) for r in all_results)
    
    all_findings = []
    for r in files_with_typehash:
        for f in r.get('findings', []):
            all_findings.append({
                'file': r['file'],
                **f,
            })
    
    # Classify findings
    valid = 0
    invalid = 0
    undetermined = 0
    error_categories = defaultdict(int)
    error_examples = defaultdict(list)
    
    for f in all_findings:
        if f['validation']['is_valid'] is True:
            valid += 1
        elif f['validation']['is_valid'] is False:
            invalid += 1
            for err in f['validation']['errors']:
                error_categories[err['type']] += 1
                if len(error_examples[err['type']]) < 3:
                    error_examples[err['type']].append({
                        'file': f['file'],
                        'typehash': f['typehash_str'],
                        'details': err['details'],
                    })
        else:
            undetermined += 1
    
    determinable = valid + invalid
    error_rate = (invalid / determinable * 100) if determinable > 0 else 0
    
    report = f"""============================================================
EIP-712 TYPEHASH Validation Report
============================================================

Summary:
  Files analyzed:           {total_files}
  Files with TYPEHASH:      {len(files_with_typehash)}
  Total TYPEHASH constants: {total_typehashes}
  Determinable:             {determinable}
    Valid:                  {valid} ({valid/determinable*100:.1f}% of determinable)
    Invalid (errors):       {invalid} ({error_rate:.1f}% of determinable)
  Undetermined:             {undetermined}

  ** ERROR RATE: {error_rate:.1f}% **

Error Breakdown:
"""
    
    for cat, count in sorted(error_categories.items(), key=lambda x: -x[1]):
        report += f"  {cat}: {count}\n"
        for ex in error_examples[cat]:
            report += f"    - {ex['file']}\n"
            report += f"      TYPEHASH: {ex['typehash']}\n"
            report += f"      Detail: {ex['details']}\n"
    
    report += f"""
============================================================
Detailed Findings:
============================================================
"""
    
    for f in all_findings:
        status = "✓ VALID" if f['validation']['is_valid'] is True else ("✗ ERROR" if f['validation']['is_valid'] is False else "? UNKNOWN")
        report += f"""
[{status}] {f['file']}
  TYPEHASH: {f['typehash_str']}
  Function: {f['associated_function'] or 'N/A'}
"""
        if f['validation']['errors']:
            for err in f['validation']['errors']:
                report += f"  → {err['details']}\n"
    
    return report


# ============================================================
# Main
# ============================================================

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("EIP-712 TYPEHASH Large-Scale Validator")
    print("=" * 60)
    
    # Step 1: Search GitHub
    print("\n[1/4] Searching GitHub for EIP-712 implementations...")
    repos = search_github_repos_v2()
    
    print(f"\n  Found {len(repos)} unique repositories with EIP-712 patterns.")
    
    # Save repo list
    with open(REPOS_FILE, 'w') as f:
        json.dump(repos, f, indent=2)
    
    # Step 2: Download files
    print("\n[2/4] Downloading Solidity source files...")
    download_dir = OUTPUT_DIR / "sources"
    download_dir.mkdir(exist_ok=True)
    
    downloaded = []
    for i, repo in enumerate(repos):
        # Construct raw URL - try main branch first, then master
        raw_url = f"https://raw.githubusercontent.com/{repo['repo']}/main/{repo['path']}"
        
        safe_name = repo['repo'].replace('/', '_') + '_' + repo['path'].replace('/', '_')
        out_path = download_dir / f"{i:04d}_{safe_name}"
        
        if download_file(raw_url, out_path):
            downloaded.append({'repo': repo, 'path': out_path})
        else:
            # Try master branch
            raw_url = f"https://raw.githubusercontent.com/{repo['repo']}/master/{repo['path']}"
            if download_file(raw_url, out_path):
                downloaded.append({'repo': repo, 'path': out_path})
        
        if (i + 1) % 20 == 0:
            print(f"  Downloaded {len(downloaded)}/{i+1}...")
        time.sleep(0.5)  # Rate limit
    
    print(f"  Successfully downloaded: {len(downloaded)}/{len(repos)}")
    
    # Step 3: Analyze
    print("\n[3/4] Analyzing TYPEHASH constants...")
    results = []
    for item in downloaded:
        result = analyze_file(item['path'])
        result['repo'] = item['repo']['repo']
        result['repo_url'] = item['repo']['url']
        results.append(result)
    
    # Save results
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Step 4: Generate report
    print("\n[4/4] Generating report...")
    report = generate_report(results)
    
    report_path = OUTPUT_DIR / "REPORT.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\nReport saved to: {report_path}")
    print(f"Results saved to: {RESULTS_FILE}")


if __name__ == '__main__':
    main()
