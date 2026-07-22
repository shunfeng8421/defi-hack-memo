#!/usr/bin/env python3
"""
DeFi 50 + Solana 8 = 58-Pattern Automated Scanner
Scans Solidity (.sol) + Rust/Anchor (.rs) code against all 58 attack patterns.
Author: Shiqiang Chen — July 2026
"""
import os, re, json, sys
from collections import defaultdict

# ============================================================
# 50 DeFi + 8 Solana Attack Patterns
# ============================================================
PATTERNS = {
    # === Flash Loan Based ===
    1: {
        "name": "Flash Loan + Price Oracle",
        "severity": "CRITICAL",
        "regex": [r'getReserves\(\)', r'getPriceOfOnePoolToken', r'balanceOf\(.*\).*price', r'spot.*price'],
        "keyword": ["getReserves", "spotPrice", "getPriceOfOne"],
        "description": "Instantaneous AMM price used in valuation — manipulable via flash loan",
        "fix": "Use TWAP oracle (Uniswap V2 `consult()`) or Chainlink price feed"
    },
    2: {
        "name": "Reentrancy (CEI Violation)",
        "severity": "CRITICAL",
        "regex": [r'\.call\{.*\}.*before.*=', r'safeTransfer.*before.*delete'],
        "keyword": ["nonReentrant", "reentrancyGuard", "unchecked"],
        "description": "External call before state update — reentrancy attack vector",
        "fix": "Follow Checks-Effects-Interactions pattern; use ReentrancyGuard"
    },
    3: {
        "name": "Flash Loan + Reentrancy Combo",
        "severity": "CRITICAL",
        "regex": [r'flashloan.*reenter|flash.*callback'],
        "keyword": ["flashLoan", "executeOperation", "onFlashLoan"],
        "description": "Flash loan callback can trigger reentrancy",
        "fix": "Lock flash loan state before callback execution"
    },
    4: {
        "name": "TWAP Oracle Manipulation",
        "severity": "HIGH",
        "regex": [r'consult\(.*0\)', r'getPrice\(\)'],
        "keyword": ["consult", "TWAP", "timeWeighted"],
        "description": "Short TWAP window still manipulable via multi-block attack",
        "fix": "Use minimum 30-minute TWAP window"
    },
    5: {
        "name": "ERC-4626 Inflation Attack",
        "severity": "HIGH",
        "regex": [r'convertToShares.*totalAssets.*totalSupply'],
        "keyword": ["totalAssets", "totalSupply", "convertToShares", "4626"],
        "description": "First depositor inflates shares via direct token donation",
        "fix": "Mint dead shares on initialization or enforce minDeposit"
    },

    # === Lending / Liquidation ===
    6: {
        "name": "Lending Liquidation Manipulation",
        "severity": "HIGH",
        "regex": [r'liquidate\(.*price', r'liquidation.*oracle'],
        "keyword": ["liquidate", "healthFactor", "collateralFactor"],
        "description": "Liquidation triggered by manipulated oracle price",
        "fix": "Use robust oracle; add liquidation grace period"
    },
    7: {
        "name": "AMM Reserve Manipulation",
        "severity": "HIGH",
        "regex": [r'getReserves\(\)', r'\.sync\(\)', r'reserve0.*reserve1'],
        "keyword": ["sync", "skim", "getReserves", "mint", "burn"],
        "description": "AMM pool reserves manipulated via flash swap",
        "fix": "Use cumulative price oracles; validate reserve ratios"
    },
    8: {
        "name": "Governance Attack",
        "severity": "CRITICAL",
        "regex": [r'propose.*calldata|execute.*proposal'],
        "keyword": ["governor", "propose", "execute", "quorum", "vote"],
        "description": "Flash loan captures governance; malicious proposal executes",
        "fix": "Add vote lock-up period and timelock"
    },

    # === Precision / Arithmetic ===
    9: {
        "name": "Rate/Incentive Manipulation",
        "severity": "MEDIUM",
        "regex": [r'reward.*rate.*total|apr.*calculation'],
        "keyword": ["rewardRate", "apr", "apy", "incentive"],
        "description": "Reward rate can be manipulated by depositing/withdrawing",
        "fix": "Use time-weighted cumulative reward tracking"
    },
    10: {
        "name": "Integer Overflow/Underflow",
        "severity": "MEDIUM",
        "regex": [r'unchecked\s*\{', r'pragma.*0\.(7|6)'],
        "keyword": ["unchecked", "SafeMath", "0.6", "0.7"],
        "description": "Pre-0.8.0 Solidity without SafeMath or unchecked block",
        "fix": "Use Solidity 0.8+ or SafeMath library"
    },
    11: {
        "name": "Division Before Multiplication",
        "severity": "LOW",
        "regex": [r'[a-zA-Z].*\/\s.*\*', r'\.div\(.*\)\.mul\('],
        "keyword": ["div", "mul", "precision", "rounding"],
        "description": "Truncation from division before multiplication",
        "fix": "Multiply first, then divide: (a * c) / b instead of (a / b) * c"
    },

    # === Access Control ===
    12: {
        "name": "Missing Access Control",
        "severity": "HIGH",
        "regex": [r'function\s+\w+.*public.*transfer', r'function\s+\w+.*public.*mint'],
        "keyword": ["onlyOwner", "require(msg.sender", "access", "role"],
        "description": "Sensitive function lacks access control modifier",
        "fix": "Add onlyOwner or role-based access control"
    },
    13: {
        "name": "Admin Key / Privilege Escalation",
        "severity": "HIGH",
        "regex": [r'onlyOwner.*upgrade|setImplementation|setAdmin'],
        "keyword": ["upgrade", "implementation", "proxy", "UUPS"],
        "description": "Admin can upgrade to malicious implementation",
        "fix": "Use timelock + multisig for upgrade authorization"
    },
    14: {
        "name": "Self-Destruct Backdoor",
        "severity": "CRITICAL",
        "regex": [r'selfdestruct', r'suicide\('],
        "keyword": ["selfdestruct", "suicide"],
        "description": "Contract can be destroyed, freezing all funds",
        "fix": "Remove selfdestruct or restrict to governance timelock"
    },

    # === Authorization ===
    15: {
        "name": "Permit/Approve Front-running",
        "severity": "MEDIUM",
        "regex": [r'permit\(.*deadline|approve\(.*amount'],
        "keyword": ["permit", "approve", "allowance", "deadline", "EIP-2612"],
        "description": "Permit without deadline allows signature replay",
        "fix": "Always include and validate deadline parameter"
    },

    # === Economic / Tokenomics ===
    16: {
        "name": "Token Burn / Deflation Attack",
        "severity": "HIGH",
        "regex": [r'transfer.*burn|_burn.*pair|burn.*uniswap'],
        "keyword": ["burn", "deflation", "reflect", "tax"],
        "description": "Transfer triggers burn of AMM pair tokens",
        "fix": "Exclude AMM pair addresses from burning logic"
    },
    17: {
        "name": "Mint/Burn Asymmetry",
        "severity": "MEDIUM",
        "regex": [r'mint\(.*amount.*\).*burn\(.*amount'],
        "keyword": ["mint", "burn", "supply", "inflation"],
        "description": "Mint and burn functions use different accounting",
        "fix": "Ensure mint and burn maintain invariant"
    },
    18: {
        "name": "Fee Manipulation",
        "severity": "MEDIUM",
        "regex": [r'setFee|updateFee|feeRate.*external'],
        "keyword": ["fee", "commission", "spread", "slippage"],
        "description": "Fee parameters can be changed without timelock",
        "fix": "Add timelock to fee updates"
    },

    # === Cross-Chain ===
    19: {
        "name": "Cross-Chain Replay",
        "severity": "CRITICAL",
        "regex": [r'ECDSA\.recover.*!chainid|recover.*!chainId'],
        "keyword": ["bridge", "cross", "chain", "layerzero", "wormhole"],
        "description": "Signed message valid on all chains — replayable",
        "fix": "Include chainId and nonce in signed message"
    },
    20: {
        "name": "Bridge Arbitrary Call",
        "severity": "CRITICAL",
        "regex": [r'\.call\{.*\}.*user|target.*call.*data'],
        "keyword": ["bridge", "relay", "sendTo", "executeRoute"],
        "description": "Bridge can execute arbitrary calls on behalf of user",
        "fix": "Whitelist target addresses and function selectors"
    },

    # === MEV / Front-running ===
    21: {
        "name": "Sandwich Attack Surface",
        "severity": "MEDIUM",
        "regex": [r'slippage.*0|minOut.*0|amountOutMin.*0'],
        "keyword": ["slippage", "minOut", "amountOutMin", "deadline"],
        "description": "No slippage protection allows sandwich attacks",
        "fix": "Require minimum output and transaction deadline"
    },
    22: {
        "name": "Unprotected SLOAD After SSTORE",
        "severity": "LOW",
        "regex": [],
        "keyword": ["transient", "tload", "tstore"],
        "description": "New transient storage patterns may have edge cases",
        "fix": "Review EIP-1153 transient storage usage"
    },

    # === NFT ===
    23: {
        "name": "NFT Reentrancy via Callbacks",
        "severity": "HIGH",
        "regex": [r'onERC721Received.*transfer|safeTransferFrom.*callback'],
        "keyword": ["onERC721Received", "safeTransferFrom", "ERC721"],
        "description": "NFT transfer callback can trigger reentrancy",
        "fix": "Use ReentrancyGuard; update state before NFT transfers"
    },
    24: {
        "name": "NFT Auction DoS",
        "severity": "MEDIUM",
        "regex": [r'bid.*for.*loop|auction.*revert'],
        "keyword": ["auction", "bid", "refund", "withdraw"],
        "description": "Contract bidder can DoS auction refund loop",
        "fix": "Check isContract() on bidders or use pull-over-push"
    },

    # === L2 / New Patterns ===
    25: {
        "name": "L2 Sequencer Downtime",
        "severity": "MEDIUM",
        "regex": [r'sequencer|L2.*oracle|optimism.*price'],
        "keyword": ["sequencer", "L2", "optimism", "arbitrum"],
        "description": "Oracle stale during L2 sequencer downtime",
        "fix": "Check sequencer uptime feed before using prices"
    },
    26: {
        "name": "Fee-on-Transfer Token",
        "severity": "MEDIUM",
        "regex": [],
        "keyword": ["safeTransferFrom","balanceOf","received"],
        "description": "Does not verify actual received amount for fee tokens",
        "fix": "Use balance-diff: before/after balanceOf to get actual received"
    },
    27: {
        "name": "EIP-712 Type Mismatch",
        "severity": "HIGH",
        "regex": [r'TYPEHASH.*uint256\[\]', r'TYPEHASH.*address\[\]'],
        "keyword": ["TYPEHASH","EIP712","typedDataV4"],
        "description": "TYPEHASH argument type doesn't match actual parameter type",
        "fix": "Ensure TYPEHASH string matches function parameter types exactly"
    },
    28: {
        "name": "Unprotected Initializer",
        "severity": "HIGH",
        "regex": [r'function\s+initialize.*public\b(?!.*initializer)'],
        "keyword": ["initialize","init(","initializer"],
        "description": "initialize() can be called by anyone without modifier",
        "fix": "Use OpenZeppelin initializer modifier"
    },
    29: {
        "name": "Multicall Authorization Trap",
        "severity": "HIGH",
        "regex": [r'multicall.*delegatecall|multicall.*\.call\{'],
        "keyword": ["multicall","batchCall","executeBatch"],
        "description": "Multicall can execute transferFrom if victim approved",
        "fix": "Validate target addresses in multicall; never approve multicall contracts"
    },
    30: {
        "name": "CREATE2 Front-Running",
        "severity": "MEDIUM",
        "regex": [r'CREATE2.*salt\b(?!.*msg\.sender)|create2.*\bsalt\b(?!.*msg\.sender)'],
        "keyword": ["create2","CREATE2","new.*salt","deploy.*salt"],
        "description": "CREATE2 salt without msg.sender allows front-running",
        "fix": "Include msg.sender in salt to prevent front-running"
    },
    31: {"name":"Rebase Attack","severity":"HIGH","regex":[],"keyword":["rebase","totalSupply","index()","gonsForBalance"],"description":"Rebase-based tokens can be manipulated via timing attacks","fix":"Snapshot balances before rebase; use cumulative tracking"},
    32: {"name":"TWAP Window Too Short","severity":"MEDIUM","regex":[r'consult\(.*0\)',r'TWAP.*10.*minute'],"keyword":["TWAP","consult","cumulativePrice"],"description":"Short TWAP window still manipulable","fix":"Use minimum 30-minute TWAP window"},
    33: {"name":"Stale Oracle","severity":"HIGH","regex":[r'latestRoundData\(\)(?!.*updatedAt)'],"keyword":["latestRoundData","updatedAt","staleness","sequencer"],"description":"Oracle data used without staleness check","fix":"Check updatedAt timestamp; revert if stale"},
    34: {"name":"Flash Loan Governance Attack","severity":"CRITICAL","regex":[r'getVotes',r'governance.*flash'],"keyword":["governance","propose","vote","quorum","snapshot"],"description":"Voting power based on current balance (manipulable via flash loan)","fix":"Snapshot voting power at block of proposal creation"},
    35: {"name":"Intentional Backdoor / Hidden Owner Path","severity":"CRITICAL","regex":[r'onlyOwner.*burn|ownerBurn|triggerBurn'],"keyword":["ownerBurn","backdoor","hiddenOwner","onlyOwner"],"description":"Owner-only burn/transfer function suggests intentional backdoor path","fix":"Require timelock + multi-sig for critical owner functions"},
    36: {"name":"Precision Amplification via Fee/Decimal Error","severity":"HIGH","regex":[r'fee.*\\*.*10000|fee.*bps.*1e18'],"keyword":["feeRateWad","basisPoints","feePrecision","dpScale"],"description":"Fee rate misinterpreted — wad vs basis points vs decimals","fix":"Document and validate fee precision; use SafeMath"},
    37: {"name":"Deposit Lock (No Withdraw)","severity":"HIGH","regex":[r'function deposit.*payable(?!.*function withdraw)'],"keyword":["deposit","balances[","!withdraw"],"description":"Deposit function exists but no withdraw — funds locked","fix":"Always provide a corresponding withdraw function"},
    38: {"name":"Hardcoded Gas Limit","severity":"LOW","regex":[r'\.transfer\(|\.send\('],"keyword":[".transfer(",".send(","2300"],"description":"transfer() only forwards 2300 gas — breaks complex receivers","fix":"Use call{value: amount}(\"\") instead of transfer/send"},
    39: {"name":"Token Migration Hijack","severity":"HIGH","regex":[r'migrate.*burn\(|migrate.*transfer\(.*msg'],"keyword":["migrate","migration","oldToken","newToken"],"description":"Token migration can be hijacked if old token not validated","fix":"Validate old token address is trusted"},
    40: {"name":"Phantom Fallback","severity":"MEDIUM","regex":[r'fallback\(\).*payable.*\{',r'fallback.*external'],"keyword":["fallback","receive","payable"],"description":"Fallback accepts any call silently — can lock funds","fix":"Revert or explicitly handle expected calls only"},
    41: {"name":"Unsafe Delegatecall Target","severity":"CRITICAL","regex":[r'\.delegatecall|DELEGATECALL'],"keyword":["delegatecall","DELEGATECALL","_impl","_target"],"description":"Delegatecall to user-controlled address","fix":"Use immutable implementation; restrict upgrade to timelock"},
    42: {"name":"Selfdestruct Backdoor","severity":"CRITICAL","regex":[r'selfdestruct|suicide\('],"keyword":["selfdestruct","suicide","kill("],"description":"Contract can be destroyed, freezing all funds","fix":"Remove selfdestruct or restrict to timelocked governance"},
    43: {"name":"Diamond Inheritance Ambiguity","severity":"LOW","regex":[r'is\s+\w+,\s*\w+.*is\s+\w+'],"keyword":["virtual","override","diamond","inheritance"],"description":"Multiple inheritance may cause storage collision","fix":"Explicitly override; use diamond storage pattern"},
    44: {"name":"Unsafe Type Cast","severity":"MEDIUM","regex":[r'uint128\(uint256|uint64\(uint256|uint32\(uint256'],"keyword":["uint128(","uint64(","uint32(","cast"],"description":"Downcast can silently truncate values","fix":"Check value before downcast; use SafeCast"},
    45: {"name":"Ownership Renounce Risk","severity":"MEDIUM","regex":[r'renounceOwnership|renounce\(\)'],"keyword":["renounceOwnership","renounce","owner = address(0)"],"description":"Renouncing ownership permanently locks admin functions","fix":"Use two-step transfer instead of renounce"},
    46: {"name":"Flash Fee Bypass","severity":"HIGH","regex":[r'flashLoan.*fee|flashloan.*fee.*!token'],"keyword":["flashLoan","flashloan","fee","premium"],"description":"Flash loan fee can be bypassed via token manipulation","fix":"Calculate fee in base token; validate repay amount"},
    47: {"name":"Fee Parameter Override","severity":"MEDIUM","regex":[r'setFee|updateFee.*external'],"keyword":["setFee","updateFee","feeBps","feeRate"],"description":"Fee parameters changeable mid-transaction","fix":"Add timelock or block fee changes during active operations"},
    48: {"name":"Loan Origination Race","severity":"HIGH","regex":[r'borrow.*price|loan.*price.*before'],"keyword":["borrow","price","collateral","checkBefore"],"description":"Price checked before collateral transferred","fix":"Update collateral first, then check price"},
    49: {"name":"Batch Transfer DoS","severity":"MEDIUM","regex":[r'for.*transfer|batch.*transfer.*for'],"keyword":["batch","for(","transfer(","loop"],"description":"One failing transfer reverts entire batch","fix":"Use try-catch or pull-over-push pattern"},
    50: {"name":"Unbounded Loop","severity":"MEDIUM","regex":[r'for.*\.length(?!.*max)'],"keyword":["for(",".length","array","loop"],"description":"Loop without max iterations can exceed gas limit","fix":"Add max iterations or paginated processing"},
    # === Solana/Anchor (51-58) ===
    51: {"name":"Solana Missing Signer","severity":"CRITICAL","regex":[r'pub fn'],"keyword":["AccountInfo","signer"],"description":"Solana instruction without signer check — anyone can call","fix":"Add #[account(signer)] attribute"},
    52: {"name":"Solana PDA Collision","severity":"HIGH","regex":[r'find_program_address'],"keyword":["PDA","seeds","bump"],"description":"PDA seeds without unique identifier — collision risk","fix":"Include user pubkey + unique nonce in seeds"},
    53: {"name":"Solana CPI Missing Signer Seeds","severity":"HIGH","regex":[r'CpiContext::new'],"keyword":["CpiContext","invoke_signed","signer_seeds"],"description":"CPI call without proper signer seeds","fix":"Pass signer_seeds for PDA authority"},
    54: {"name":"Solana Unchecked Account Data","severity":"HIGH","regex":[r'try_borrow_mut_data'],"keyword":["AccountInfo","deserialize"],"description":"Account data used without Anchor validation","fix":"Use #[account] macro for type safety"},
    55: {"name":"Solana Slot as Time Source","severity":"MEDIUM","regex":[r'.slot'],"keyword":["Clock::get","slot","unix_timestamp"],"description":"Using slot as time source — non-deterministic","fix":"Use Clock::get()?.unix_timestamp instead of .slot"},
    56: {"name":"Solana HasOne Missing","severity":"HIGH","regex":[r'#\[derive\(Accounts\)'],"keyword":["has_one","belongs_to","owner"],"description":"Account struct without ownership constraint","fix":"Add #[account(has_one = owner)]"},
    57: {"name":"Solana Unchecked Arithmetic","severity":"MEDIUM","regex":[r'\+=|\-='],"keyword":["checked_add","saturating_add","overflow"],"description":"No overflow protection on arithmetic","fix":"Use checked_add/checked_sub or saturating variants"},
    58: {"name":"Solana Token CPI Unvalidated","severity":"HIGH","regex":[r'token::transfer|spl_token'],"keyword":["token::transfer","spl_token","validate"],"description":"Token CPI without prior account validation","fix":"Verify token account ownership + mint before CPI"},
}


# ============================================================
# Scanner Engine
# ============================================================
class DeFiScanner:
    def __init__(self, target_dir):
        self.target_dir = target_dir
        self.results = defaultdict(list)
        self.stats = {"files": 0, "lines": 0, "findings": 0}

    def scan_file(self, filepath):
        try:
            with open(filepath, encoding='utf-8', errors='replace') as f:
                source = f.read()
        except:
            return
        
        self.stats["files"] += 1
        self.stats["lines"] += source.count('\n')
        
        for pid, pattern in PATTERNS.items():
            found = False
            # Check regex patterns
            for regex in pattern["regex"]:
                matches = re.findall(regex, source, re.IGNORECASE)
                if matches:
                    found = True
                    break
            # Check keywords (both present and absent cases)
            if not found:
                for kw in pattern["keyword"]:
                    if kw.startswith('!'):
                        if kw[1:] not in source.lower():
                            found = True
                            break
                    elif kw.lower() in source.lower():
                        found = True
                        break
            
            if found:
                # Find exact line numbers
                lines = source.split('\n')
                line_nums = []
                for i, line in enumerate(lines, 1):
                    for regex in pattern["regex"]:
                        if re.search(regex, line, re.IGNORECASE):
                            line_nums.append(i)
                            break
                
                self.results[filepath].append({
                    "id": pid,
                    "name": pattern["name"],
                    "severity": pattern["severity"],
                    "description": pattern["description"],
                    "fix": pattern["fix"],
                    "lines": line_nums[:3]  # max 3 line refs
                })
                self.stats["findings"] += 1

    def scan_directory(self):
        for dirpath, _, filenames in os.walk(self.target_dir):
            for fn in filenames:
                if fn.endswith('.sol') or fn.endswith('.rs'):
                    self.scan_file(os.path.join(dirpath, fn))

    def generate_report(self):
        lines = []
        lines.append("=" * 60)
        lines.append(f"DeFi 50-Pattern Scan Report")
        lines.append(f"Target: {self.target_dir}")
        lines.append(f"Files: {self.stats['files']} | Lines: {self.stats['lines']} | Findings: {self.stats['findings']}")
        lines.append("=" * 60)
        
        if not self.results:
            lines.append("\n✅ No issues found!")
            return '\n'.join(lines)
        
        for filepath, findings in sorted(self.results.items()):
            rel_path = os.path.relpath(filepath, self.target_dir)
            lines.append(f"\n📄 {rel_path}")
            for f in sorted(findings, key=lambda x: x['id']):
                sev_icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🔵'}.get(f['severity'], '⚪')
                lines.append(f"  {sev_icon} [{f['id']:02d}] {f['name']} ({f['severity']})")
                lines.append(f"      {f['description']}")
                if f['lines']:
                    lines.append(f"      Lines: {', '.join(map(str, f['lines']))}")
                lines.append(f"      Fix: {f['fix']}")
        
        lines.append(f"\n{'=' * 60}")
        lines.append(f"Scanned with 58 detection rules (covering 50 DeFi + 8 Solana patterns)")
        lines.append(f"  Flash Loan Suite: 8 patterns (Spot/TWAP/Governance/Lend/Burn/Bridge/Precision/Backdoor)")
        return '\n'.join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python defi-scanner.py <target_directory>")
        sys.exit(1)
    
    scanner = DeFiScanner(sys.argv[1])
    scanner.scan_directory()
    print(scanner.generate_report())
    
    # Save JSON
    json_path = os.path.join(sys.argv[1] if os.path.isdir(sys.argv[1]) else '.', 'scan-results.json')
    with open(json_path, 'w') as f:
        json.dump(dict(scanner.results), f, indent=2)
    print(f"\nJSON results: {json_path}")
