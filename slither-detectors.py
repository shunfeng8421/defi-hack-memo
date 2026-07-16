"""
Slither Detector #5: CEI Violation — Checks-Effects-Interactions pattern breaker
Pattern #2: Reentrancy
Examples: JoeAgent $45K, LendfMe $25M, Cream $130M
"""
from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification

class CEIViolationDetector(AbstractDetector):
    ARGUMENT = "cei-violation"
    HELP = "External call before state update (CEI violation)"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH
    WIKI = "https://github.com/shunfeng8421/defi-hack-memo"
    WIKI_TITLE = "CEI-Violation"
    WIKI_DESCRIPTION = "Reentrancy: state updated AFTER external call"

    def _detect(self):
        results = []
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                # Find external calls (transfer, call, send)
                external_calls = []
                state_writes = []
                
                for node in function.nodes:
                    for ir in node.irs:
                        if hasattr(ir, 'call_value') or 'transfer' in str(ir).lower():
                            external_calls.append(node.node_id)
                        if hasattr(ir, 'lvalue') and ir.lvalue:
                            state_writes.append(node.node_id)
                
                # Check if any external call comes before a state write
                for ec in external_calls:
                    for sw in state_writes:
                        if ec < sw:
                            results.append(self.generate_result([
                                f"CEI violation in {function.name} @ {contract.name}",
                                "External call BEFORE state update — reentrancy possible",
                                "Pattern #2: Move state updates before external calls"
                            ]))
                            break
                    if results: break
        
        return results


"""
Slither Detector #7: Missing Access Control
Pattern #8: Governance / Permission Attack
Examples: TempleDAO $2.3M, TeamFinance $15.8M, Ronin $600M
"""
class MissingAccessControlDetector(AbstractDetector):
    ARGUMENT = "missing-access-control"
    HELP = "Public/external function without access control"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.MEDIUM
    WIKI = "https://github.com/shunfeng8421/defi-hack-memo"
    WIKI_TITLE = "Missing-Access-Control"
    WIKI_DESCRIPTION = "Sensitive function missing onlyOwner/role check"

    def _detect(self):
        results = []
        ACCESS_MODIFIERS = {'onlyOwner', 'onlyGovernor', 'onlyAdmin', 'onlyRole',
                           'onlyVault', 'onlyPolicy', 'onlyGuardian', 'require'}
        
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                if function.visibility not in ['public', 'external']:
                    continue
                if function.is_constructor or function.is_fallback:
                    continue
                
                has_access = any(
                    any(m in str(mod).lower() for m in ACCESS_MODIFIERS)
                    for mod in function.modifiers
                )
                
                # Find functions that do token transfers or state changes
                keywords = ['transfer', 'mint', 'burn', 'withdraw', 'set', 'update']
                has_sensitive = any(k in function.name.lower() for k in keywords)
                
                if has_sensitive and not has_access:
                    results.append(self.generate_result([
                        f"Missing access control: {function.name} in {contract.name}",
                        "Function changes state but has no access modifier",
                        "Pattern #8: Consider adding onlyOwner or role check"
                    ]))
        
        return results


"""
Slither Detector #10: Permit Front-running
Pattern #15: Authorization Trap
Examples: SquidMulticall $800K, Seneca $6M
"""
class PermitFrontrunDetector(AbstractDetector):
    ARGUMENT = "permit-frontrun"
    HELP = "EIP-2612 permit without deadline protection"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.MEDIUM
    WIKI = "https://github.com/shunfeng8421/defi-hack-memo"
    WIKI_TITLE = "Permit-Frontrun"
    WIKI_DESCRIPTION = "permit() without deadline allows signature replay"

    def _detect(self):
        results = []
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                if 'permit' not in function.name.lower():
                    continue
                source = function.source_code.lower()
                if 'deadline' not in source:
                    results.append(self.generate_result([
                        f"Permit without deadline: {function.name} in {contract.name}",
                        "Missing deadline parameter allows signature replay",
                        "Pattern #15: Add deadline check to prevent front-running"
                    ]))
        
        return results


"""
Slither Detector #4: ERC-4626 Inflation Attack
Pattern #5: Deposit Donation Inflation
Examples: vault-core
"""
class ERC4626InflationDetector(AbstractDetector):
    ARGUMENT = "erc4626-inflation"
    HELP = "ERC-4626 vault vulnerable to donation inflation attack"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH
    WIKI = "https://github.com/shunfeng8421/defi-hack-memo"
    WIKI_TITLE = "ERC4626-Inflation"
    WIKI_DESCRIPTION = "First depositor can inflate shares via direct token donation"

    def _detect(self):
        results = []
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                if function.name not in ['deposit', 'mint']:
                    continue
                source = function.source_code
                # Check for ERC-4626 deposit pattern without minDeposit
                has_total_assets = 'totalAssets' in source or 'totalSupply' in source
                has_division = '/' in source
                has_min_deposit = 'minDeposit' in source or 'MIN_DEPOSIT' in source or 'deadShares' in source
                
                if has_total_assets and has_division and not has_min_deposit:
                    results.append(self.generate_result([
                        f"ERC-4626 inflation risk: {function.name} in {contract.name}",
                        "No minDeposit/deadShares protection",
                        "Pattern #5: First depositor can inflate shares via donation"
                    ]))
        
        return results


"""
Slither Detector #8: Precision Rounding Loss
Pattern #46: Arithmetic Precision
Examples: BEC $1.5B, PancakeBunny $120M
"""
class PrecisionRoundingDetector(AbstractDetector):
    ARGUMENT = "precision-rounding"
    HELP = "Division before multiplication causing precision loss"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.LOW
    WIKI = "https://github.com/shunfeng8421/defi-hack-memo"
    WIKI_TITLE = "Precision-Rounding"
    WIKI_DESCRIPTION = "a / b * c should be a * c / b to avoid truncation"

    def _detect(self):
        results = []
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                source = function.source_code
                # Pattern: division before multiplication
                lines = source.split('\n')
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if '/ ' in stripped and '* ' in stripped:
                        div_pos = stripped.find('/ ')
                        mul_pos = stripped.find('* ')
                        if div_pos < mul_pos:
                            if 'Math.mulDiv' not in source and 'mulDiv' not in source:
                                results.append(self.generate_result([
                                    f"Precision loss: {function.name}:{i} in {contract.name}",
                                    f"  {stripped[:60]}",
                                    "Pattern #46: Division before multiplication causes truncation"
                                ]))
        
        return results
