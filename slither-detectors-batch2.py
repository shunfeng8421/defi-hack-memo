"""
Batch 2: Slither Detectors #6, #9, #11-14
"""
from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification

class GovernanceFlashLoanDetector(AbstractDetector):
    """#6: Flash loan used to capture governance — Beanstalk $182M, Cork $12M"""
    ARGUMENT = "governance-flashloan"
    HELP = "Governance function callable after flash loan"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.MEDIUM
    WIKI = "https://github.com/shunfeng8421/defi-hack-memo"

    def _detect(self):
        results = []
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                source = function.source_code.lower()
                if ('propose' in source or 'vote' in source or 'execute' in source):
                    if 'flash' not in source and 'lock' not in source and 'timelock' not in source:
                        results.append(self.generate_result([
                            f"Governance without timelock: {function.name} in {contract.name}",
                            "Pattern #11: Flash loan can capture voting power"
                        ]))
        return results


class DelegatecallAbuseDetector(AbstractDetector):
    """#9: delegatecall to user-controlled address — Parity $170M"""
    ARGUMENT = "delegatecall-abuse"
    HELP = "delegatecall with user-controlled target"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH
    WIKI = "https://github.com/shunfeng8421/defi-hack-memo"

    def _detect(self):
        results = []
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                source = function.source_code
                if 'delegatecall' in source and 'msg.sender' not in source:
                    if any(param in source for param in ['_target', '_impl', '_addr']):
                        results.append(self.generate_result([
                            f"Unsafe delegatecall: {function.name} in {contract.name}",
                            "Pattern #13: delegatecall to potentially user-controlled address"
                        ]))
        return results


class CrossChainReplayDetector(AbstractDetector):
    """#11: Cross-chain message without chainId — Poly $610M, Nomad $152M"""
    ARGUMENT = "cross-chain-replay"
    HELP = "Cross-chain message without chainId replay protection"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH
    WIKI = "https://github.com/shunfeng8421/defi-hack-memo"

    def _detect(self):
        results = []
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                if 'bridge' not in contract.name.lower() and 'cross' not in contract.name.lower():
                    continue
                source = function.source_code
                if ('send' in function.name.lower() or 'process' in function.name.lower()):
                    if 'chainid' not in source.lower() and 'chainId' not in source:
                        results.append(self.generate_result([
                            f"Cross-chain no chainId: {function.name} in {contract.name}",
                            "Pattern #34: Add block.chainid to prevent cross-chain replay"
                        ]))
        return results


class TokenBurnManipulationDetector(AbstractDetector):
    """#12: Token transfer triggers AMM pair burn — BabyDoge $7.5M, AIDC"""
    ARGUMENT = "token-burn-manipulation"
    HELP = "Transfer triggers burn that affects AMM pair"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.LOW
    WIKI = "https://github.com/shunfeng8421/defi-hack-memo"

    def _detect(self):
        results = []
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                if function.name not in ['transfer', '_transfer']:
                    continue
                source = function.source_code
                if 'burn' in source and ('pair' in source or 'pool' in source or 'uniswap' in source.lower()):
                    results.append(self.generate_result([
                        f"Burn in transfer: {function.name} in {contract.name}",
                        "Pattern #25: Transfer triggering AMM pair burn can be exploited"
                    ]))
        return results


class FeeOnTransferDetector(AbstractDetector):
    """#13: Assumes transfer sends exact amount — RadiantCapital $4.5M"""
    ARGUMENT = "fee-on-transfer"
    HELP = "Balance check without accounting for transfer fees"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.LOW
    WIKI = "https://github.com/shunfeng8421/defi-hack-memo"

    def _detect(self):
        results = []
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                source = function.source_code
                has_transfer = 'transfer(' in source or 'transferFrom(' in source or 'safeTransfer' in source
                has_balance_check = 'balanceOf' in source and ('before' in source.lower() or 'after' in source.lower())
                
                if has_transfer and not has_balance_check:
                    if 'amount' in source:
                        results.append(self.generate_result([
                            f"Fee-on-transfer risk: {function.name} in {contract.name}",
                            "Pattern #39: Use balance-diff instead of amount for fee-on-transfer tokens"
                        ]))
        return results


class UpgradeStorageCollisionDetector(AbstractDetector):
    """#14: UUPS upgradeable without storage gap — ThunderLoan"""
    ARGUMENT = "upgrade-storage-collision"
    HELP = "Upgradeable contract missing __gap for storage safety"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.LOW
    WIKI = "https://github.com/shunfeng8421/defi-hack-memo"

    def _detect(self):
        results = []
        for contract in self.compilation_unit.contracts_derived:
            is_upgradeable = any('Upgradeable' in str(parent) or 'UUPS' in str(parent) 
                               for parent in contract.inheritance)
            if not is_upgradeable:
                continue
            
            has_gap = any('__gap' in str(var.name) for var in contract.state_variables)
            if not has_gap:
                results.append(self.generate_result([
                    f"Missing storage gap: {contract.name} (UUPS upgradeable)",
                    "Pattern #13: Add uint256[50] __gap for upgrade safety"
                ]))
        
        return results
