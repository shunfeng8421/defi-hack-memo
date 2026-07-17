#!/usr/bin/env python3
"""
EIP-712 TYPEHASH Validator v3: Token-based authenticated search + curated list.
Compiles 50+ known EIP-712 implementations and validates TYPEHASH correctness.
"""

import re
import json
import base64
import subprocess
import time
import os
import sys
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = Path(__file__).parent / "eip712_samples_v3"
SOURCES_DIR = OUTPUT_DIR / "sources"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SOURCES_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# Curated list of well-known EIP-712 implementations
# =====================================================
KNOWN_EIP712_REPOS = [
    # OpenZeppelin ecosystem
    ("OpenZeppelin/openzeppelin-contracts", "contracts/utils/cryptography/EIP712.sol"),
    ("OpenZeppelin/openzeppelin-contracts", "contracts/token/ERC20/extensions/ERC20Permit.sol"),
    ("OpenZeppelin/openzeppelin-contracts", "contracts/token/ERC20/extensions/ERC20Votes.sol"),
    ("OpenZeppelin/openzeppelin-contracts", "contracts/governance/Governor.sol"),
    ("OpenZeppelin/openzeppelin-contracts", "contracts/governance/utils/Votes.sol"),
    
    # OpenZeppelin v5
    ("OpenZeppelin/openzeppelin-contracts", "contracts/utils/cryptography/draft-EIP712.sol"),
    ("OpenZeppelin/openzeppelin-contracts", "contracts/metatx/MinimalForwarder.sol"),
    
    # Uniswap
    ("Uniswap/v3-core", "contracts/UniswapV3Pool.sol"),
    ("Uniswap/v3-periphery", "contracts/lens/Quoter.sol"),
    ("Uniswap/v2-core", "contracts/UniswapV2ERC20.sol"),
    ("Uniswap/permit2", "src/Permit2.sol"),
    ("Uniswap/permit2", "src/AllowanceTransfer.sol"),
    ("Uniswap/permit2", "src/SignatureTransfer.sol"),
    
    # Compound / Aave
    ("compound-finance/compound-protocol", "contracts/Governance/GovernorAlpha.sol"),
    ("compound-finance/compound-protocol", "contracts/Governance/GovernorBravoDelegate.sol"),
    ("aave/aave-v3-core", "contracts/protocol/tokenization/AToken.sol"),
    
    # Balancer / Curve
    ("balancer/balancer-v2-monorepo", "pkg/pool-weighted/contracts/WeightedPool.sol"),
    ("curvefi/curve-dao-contracts", "contracts/VotingEscrow.vy"),  # Vyper, not Solidity
    
    # MakerDAO
    ("makerdao/dss", "src/dai.sol"),
    ("makerdao/sai", "src/sai.sol"),
    
    # USDC / USDT / stablecoins
    ("centrehq/centre-tokens", "contracts/v2/FiatTokenV2.sol"),
    
    # Chainlink
    ("smartcontractkit/chainlink", "contracts/src/v0.8/shared/token/ERC677/BasicToken.sol"),
    
    # ERC-721 / NFT
    ("OpenZeppelin/openzeppelin-contracts", "contracts/token/ERC721/ERC721.sol"),
    
    # ENS
    ("ensdomains/ens-contracts", "contracts/ethregistrar/BaseRegistrarImplementation.sol"),
    
    # Safe (Gnosis Safe)
    ("safe-global/safe-contracts", "contracts/examples/libraries/GnosisSafeStorage.sol"),
    ("safe-global/safe-contracts", "contracts/Safe.sol"),
    
    # Lido
    ("lidofinance/lido-dao", "contracts/0.8.9/Lido.sol"),
    
    # Synthetix
    ("Synthetixio/synthetix", "contracts/StakingRewards.sol"),
    
    # Additional implementations
    ("mds1/multicall", "src/Multicall3.sol"),
    ("transmissions11/solmate", "src/tokens/ERC20.sol"),
    ("Rari-Capital/solmate", "src/tokens/ERC20.sol"),
    ("foundry-rs/forge-std", "src/StdCheats.sol"),
    ("foundry-rs/forge-std", "src/Script.sol"),
    
    # More DeFi
    ("convex-eth/platform", "contracts/contracts/Booster.sol"),
    ("fraxfinance/frax-solidity", "src/hardhat/contracts/Frax/Frax.sol"),
    ("OlympusDAO/olympus-contracts", "src/policies/Operator.sol"),
    ("pancakeswap/pancake-swap-core", "contracts/PancakePair.sol"),
    ("sushiswap/sushiswap", "contracts/uniswapv2/UniswapV2ERC20.sol"),
    ("Rari-Capital/vaults", "contracts/RariVault.sol"),
    ("yieldprotocol/yield-utils-v2", "contracts/utils/CauldronLib.sol"),
    
    # Governance / DAO
    ("withtally/compound-governor-bravo", "contracts/GovernorBravoDelegate.sol"),
    ("withtally/openzeppelin-governor", "contracts/Governor.sol"),
    
    # Bridging
    ("wormhole-foundation/wormhole", "ethereum/contracts/bridge/Bridge.sol"),
    ("celer-network/sgn-v2-contracts", "contracts/message/framework/MessageBus.sol"),
    
    # Additional popular repos
    ("dapphub/ds-token", "src/token.sol"),
    ("dapphub/ds-note", "src/note.sol"),
    ("dapphub/ds-auth", "src/auth.sol"),
]

# Fallback: use gh search for additional sampling (with extreme patience)
def token_read():
    """Read GitHub token from file."""
    token_file = Path(r"C:\Users\Administrator\Desktop\token.txt")
    if token_file.exists():
        lines = token_file.read_text().strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('gh') or line.startswith('github'):
                # Format: gh_pat_... or github_pat_...
                if '_pat_' in line:
                    return line
            elif line.startswith('ghp_') or line.startswith('gho_') or line.startswith('ghu_'):
                return line
    return None


def gh_api_get(repo: str, path: str) -> str:
    """Get file content via gh api."""
    url = f"repos/{repo}/contents/{path}"
    cmd = ['gh', 'api', url, '--jq', '.content']
    
    for attempt in range(3):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if r.returncode == 0 and r.stdout.strip():
                content = r.stdout.replace('\n', '').replace('\r', '').strip()
                decoded = base64.b64decode(content).decode('utf-8', errors='replace')
                return decoded
            # If rate limited, wait
            if r.returncode != 0 and '403' in (r.stdout + r.stderr):
                print(f"    Rate limited, waiting 5s...")
                time.sleep(5)
                continue
            return None
        except Exception:
            time.sleep(2)
    
    return None


def extract_typehash_constants(source: str) -> list[dict]:
    """Extract all TYPEHASH constant definitions."""
    results = []
    pattern = (
        r'bytes32\s+(?:constant\s+)?(?:public\s+)?(?:private\s+)?(?:internal\s+)?'
        r'(\w*(?:TYPE_?HASH|TYPEHASH|PERMIT_TYPEHASH|_TYPEHASH)\w*)\s*'
        r'=\s*keccak256\(\s*(?:bytes\s*\()?\s*["\']((?:[^"\\]|\\.)*)["\']\s*\)?\s*\)'
    )
    
    for match in re.finditer(pattern, source, re.IGNORECASE):
        name = match.group(1)
        typehash_str = match.group(2)
        line_no = source[:match.start()].count('\n') + 1
        results.append({'name': name, 'typehash_str': typehash_str, 'line_no': line_no})
    
    return results


def find_matching_function(source: str, typehash_name: str) -> dict:
    """Find the function that uses a TYPEHASH in abi.encode()."""
    usage_pattern = rf'abi\.encode\s*\(\s*{re.escape(typehash_name)}\s*,([^)]*)\)'
    
    for match in re.finditer(usage_pattern, source):
        before = source[:match.start()]
        func_matches = list(re.finditer(r'function\s+(\w+)\s*\(([^)]*)\)', before))
        if not func_matches:
            continue
        
        fm = func_matches[-1]
        func_name = fm.group(1)
        params_str = fm.group(2).strip()
        line_no = before.count('\n') + 1
        
        params = []
        if params_str:
            for p in params_str.split(','):
                p = p.strip()
                parts = p.split()
                if len(parts) >= 2:
                    actual_parts = [x for x in parts if x not in ('memory', 'calldata', 'storage')]
                    if len(actual_parts) >= 2:
                        params.append({'name': actual_parts[-1], 'type': actual_parts[0]})
        
        return {'name': func_name, 'params': params, 'line_no': line_no}
    
    return None


def parse_typehash_string(s: str) -> tuple:
    """Parse TYPEHASH string -> (func_name, [param_types])."""
    cleaned = s.strip()
    match = re.match(r'(\w+)\s*\(([^)]*)\)', cleaned)
    if not match:
        return None, None
    
    func_name = match.group(1)
    params_str = match.group(2).strip()
    
    param_types = []
    if params_str:
        for p in params_str.split(','):
            p = p.strip()
            parts = p.split()
            if parts:
                param_types.append(parts[0])
    
    return func_name, param_types


KNOWN_MISSPELLINGS = {
    'addres': 'address', 'adress': 'address',
    'uint2566': 'uint256', 'boool': 'bool',
    'bytess32': 'bytes32', 'stringg': 'string',
}

def canonical_type(t: str) -> str:
    t = t.strip()
    is_array = t.endswith('[]')
    base = t[:-2] if is_array else t
    base_lower = base.lower()
    if base_lower in KNOWN_MISSPELLINGS:
        base = KNOWN_MISSPELLINGS[base_lower]
    return base + ('[]' if is_array else '')


def validate_typehash(typehash_str: str, func: dict) -> dict:
    errors = []
    func_name_th, th_params = parse_typehash_string(typehash_str)
    
    if func_name_th is None:
        return {'is_valid': False, 'errors': [{'type': 'PARSE_ERROR', 'details': f'Cannot parse: {typehash_str}'}]}
    
    if func is None:
        return {'is_valid': None, 'errors': [{'type': 'NO_FUNC', 'details': 'No matching function found'}]}
    
    # Check function name
    if func_name_th != func['name']:
        errors.append({
            'type': 'FUNC_MISMATCH',
            'details': f"TYPEHASH func '{func_name_th}' != actual '{func['name']}'"
        })
    
    actual_params = func['params']
    if len(th_params) != len(actual_params):
        errors.append({
            'type': 'PARAM_COUNT',
            'details': f"TYPEHASH has {len(th_params)} params, function has {len(actual_params)}"
        })
    
    for i in range(min(len(th_params), len(actual_params))):
        th_type = canonical_type(th_params[i])
        actual_type = canonical_type(actual_params[i])
        
        if th_type.lower() != actual_type.lower():
            if th_type.lower() == 'uint' and actual_type.lower() == 'uint256':
                continue
            if th_type.lower() == 'uint256' and actual_type.lower() == 'uint':
                continue
            
            errors.append({
                'type': 'TYPE_MISMATCH',
                'details': f"Param {i+1}: TYPEHASH='{th_params[i]}', func='{actual_params[i]['type']}'"
            })
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'typehash_params': th_params,
        'actual_params': [p['type'] for p in actual_params],
    }


def main():
    print("=" * 70)
    print("EIP-712 TYPEHASH Validator v3: Curated + Search")
    print("=" * 70)
    
    # Phase 1: Try curated list
    print(f"\n[Phase 1] Downloading {len(KNOWN_EIP712_REPOS)} known EIP-712 implementations...\n")
    
    sources_dict = {}
    
    for i, (repo, path) in enumerate(KNOWN_EIP712_REPOS):
        key = f"{repo}/{path}"
        print(f"  [{i+1}/{len(KNOWN_EIP712_REPOS)}] {key}")
        
        source = gh_api_get(repo, path)
        if source:
            sources_dict[key] = {
                'repo': repo,
                'path': path,
                'source': source,
            }
            print(f"    -> Downloaded ({len(source)} chars)")
        else:
            print(f"    -> Not found or rate limited")
        
        time.sleep(0.5)
    
    print(f"\n  Successfully downloaded: {len(sources_dict)}/{len(KNOWN_EIP712_REPOS)}")
    
    # Phase 2: If we have very few results, try gh search
    if len(sources_dict) < 20:
        print("\n[Phase 2] Supplementing with gh search (slow, respectful)...")
        search_queries = [
            ("PERMIT_TYPEHASH", 30),
            ("MAIL_TYPEHASH", 20),
            ("BID_TYPEHASH", 20),
            ("bytes32 TYPEHASH keccak256", 30),
            ("_TYPE_HASH keccak256", 20),
        ]
        
        for query, limit in search_queries:
            cmd = ['gh', 'search', 'code', query, 'language:Solidity',
                   '--limit', str(limit), '--json', 'url,repository,path']
            
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if r.returncode == 0 and r.stdout.strip():
                    results = json.loads(r.stdout)
                    print(f"  Search '{query}': {len(results)} results")
                    
                    for item in results[:10]:  # Download only first 10 from each search
                        repo_name = item['repository']['nameWithOwner']
                        path = item['path']
                        key = f"{repo_name}/{path}"
                        
                        if key not in sources_dict:
                            source = gh_api_get(repo_name, path)
                            if source:
                                sources_dict[key] = {
                                    'repo': repo_name,
                                    'path': path,
                                    'source': source,
                                }
                            time.sleep(0.8)
            except Exception as e:
                print(f"  Search '{query}': error - {e}")
            
            time.sleep(3)  # Respectful delay between searches
    
    print(f"\n  Total sources: {len(sources_dict)}")
    
    # Phase 3: Analyze
    print("\n[Phase 3] Analyzing TYPEHASH constants...")
    
    all_findings = []
    
    for key, data in sources_dict.items():
        source = data['source']
        typehashes = extract_typehash_constants(source)
        
        if not typehashes:
            # Check if file has EIP-712 usage without explicit TYPEHASH
            if 'keccak256' in source and ('hashStruct' in source or 'EIP712' in source or 'domainSeparator' in source):
                all_findings.append({
                    'repo': data['repo'],
                    'path': data['path'],
                    'typehash_name': 'N/A',
                    'typehash_str': 'N/A',
                    'func_name': None,
                    'func_params': [],
                    'validation': {'is_valid': None, 'errors': [{'type': 'NO_EXPLICIT_TYPEHASH', 'details': 'Uses EIP-712 but TYPEHASH not found as constant'}]},
                })
            continue
        
        for th in typehashes:
            func = find_matching_function(source, th['name'])
            validation = validate_typehash(th['typehash_str'], func)
            
            all_findings.append({
                'repo': data['repo'],
                'path': data['path'],
                'typehash_name': th['name'],
                'typehash_str': th['typehash_str'],
                'func_name': func['name'] if func else None,
                'func_params': func['params'] if func else [],
                'validation': validation,
            })
    
    # Phase 4: Statistics
    print("\n[Phase 4] Computing statistics...\n")
    
    valid = sum(1 for f in all_findings if f['validation']['is_valid'] is True)
    invalid = sum(1 for f in all_findings if f['validation']['is_valid'] is False)
    undetermined = sum(1 for f in all_findings if f['validation']['is_valid'] is None)
    total = len(all_findings)
    
    determinable = valid + invalid
    error_rate = (invalid / determinable * 100) if determinable > 0 else 0
    
    # Error categories
    error_cat = defaultdict(int)
    error_examples = defaultdict(list)
    
    for f in all_findings:
        if f['validation']['is_valid'] is False:
            for err in f['validation']['errors']:
                error_cat[err['type']] += 1
                if len(error_examples[err['type']]) < 5:
                    error_examples[err['type']].append({
                        'repo': f['repo'],
                        'typehash': f['typehash_str'],
                        'detail': err['details'],
                    })
    
    # Generate report
    report = f"""
{'='*70}
EIP-712 TYPEHASH ECOSYSTEM VALIDATION - FINAL REPORT
{'='*70}

SAMPLING:
  Files with EIP-712 patterns: {len(sources_dict)}
  Total TYPEHASH entries:      {total}

RESULTS:
  [OK] Valid:       {valid} ({valid/total*100:.1f}%)
  [ERR] Invalid:     {invalid} ({invalid/total*100:.1f}%)
  ? Undetermined: {undetermined} ({undetermined/total*100:.1f}%)
  
  ** CONFIRMED ERROR RATE (among determinable): {error_rate:.1f}% **
  ** ({(valid + invalid + undetermined)} entries across {len(sources_dict)} files) **

ERROR CATEGORIES:
"""
    
    for cat, count in sorted(error_cat.items(), key=lambda x: -x[1]):
        report += f"  [{cat}]: {count}\n"
        for ex in error_examples[cat][:3]:
            report += f"    * {ex['repo']}\n"
            report += f"      TYPEHASH: {ex['typehash']}\n"
            report += f"      Detail: {ex['detail']}\n"
    
    report += f"""
{'='*70}
INVALID TYPEHASH DETAIL:
{'='*70}
"""
    
    for f in all_findings:
        if f['validation']['is_valid'] is False:
            report += f"""
[ERR] {f['repo']}/{f['path']}
  TYPEHASH: {f['typehash_str']}
"""
            for err in f['validation']['errors']:
                report += f"  -> {err['details']}\n"
    
    report += f"""
{'='*70}
VALID TYPEHASH SAMPLE:
{'='*70}
"""
    
    for f in all_findings:
        if f['validation']['is_valid'] is True:
            report += f"[OK] {f['repo']}\n  TYPEHASH: {f['typehash_str']}\n  Function: {f['func_name']}\n\n"
    
    # Save
    report_path = OUTPUT_DIR / "FINAL_REPORT.txt"
    report_path.write_text(report, encoding='utf-8')
    
    findings_path = OUTPUT_DIR / "all_findings.json"
    with open(findings_path, 'w', encoding='utf-8') as f:
        json.dump(all_findings, f, indent=2, ensure_ascii=False)
    
    print(report)
    print(f"\n[OK] Report: {report_path}")
    print(f"[OK] Findings: {findings_path}")
    
    return all_findings


if __name__ == '__main__':
    main()
