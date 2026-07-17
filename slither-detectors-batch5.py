"""
Slither Detectors Final Batch: 36-50 — Complete Implementations
"""
from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification

# 36: ERC777 reentrancy via tokensReceived
class ERC777Reentrancy(AbstractDetector):
    ARGUMENT = "erc777-reentrancy"
    HELP = "ERC777 send() triggers tokensReceived callback before state update"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH
    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:
                src = f.source_code
                if ('send(' in src or 'operatorSend(' in src) and 'nonReentrant' not in src:
                    if any(s in src for s in ['balance','shares','credits']):
                        results.append(self.generate_result([
                            f"ERC777 reentrancy risk: {f.name} in {c.name}",
                            "send() callback can reenter before balance updated"
                        ]))
        return results

# 37: Constructor misspelled as 'construcor'
class MisspelledConstructor(AbstractDetector):
    ARGUMENT = "misspelled-constructor"
    HELP = "Function named 'construcor' instead of 'constructor' — becomes public"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH
    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:
                if 'construcor' in f.name.lower() or 'contructor' in f.name.lower():
                    results.append(self.generate_result([
                        f"Misspelled constructor: {f.name} in {c.name}",
                        "Anyone can call this — not only at deploy time"
                    ]))
        return results

# 38: Proxy init without initializer modifier
class ProxyInitUnprotected(AbstractDetector):
    ARGUMENT = "proxy-init-unprotected"
    HELP = "initialize() callable multiple times without modifier"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH
    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:
                if 'initialize' not in f.name: continue
                src = f.source_code
                has_init = 'initializer' in src or 'onlyInitializing' in src
                has_require = 'require' in src and ('!initialized' in src.lower() or 'initialized == false' in src.lower())
                if not has_init and not has_require:
                    results.append(self.generate_result([
                        f"Unprotected init: {f.name} in {c.name}",
                        "Add initializer modifier or require(!initialized)"
                    ]))
        return results

# 39: Low-level call without success check
class UncheckedCall(AbstractDetector):
    ARGUMENT = "unchecked-call"
    HELP = ".call{} result not validated — silent failures"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.HIGH
    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:
                src = f.source_code
                if '.call{' in src and 'require(success' not in src and 'if (!success' not in src:
                    results.append(self.generate_result([
                        f"Unchecked call: {f.name} in {c.name}",
                        "Add require(success) or if(!success) revert"
                    ]))
        return results

# 40: Single-step ownership transfer
class SingleStepOwner(AbstractDetector):
    ARGUMENT = "single-step-owner"
    HELP = "transferOwnership() without acceptOwnership()"
    IMPACT = DetectorClassification.LOW
    CONFIDENCE = DetectorClassification.MEDIUM
    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            has_transfer = any('transferOwnership' in f.name for f in c.functions)
            has_accept = any('acceptOwnership' in f.name for f in c.functions)
            if has_transfer and not has_accept:
                results.append(self.generate_result([
                    f"Single-step owner: {c.name}",
                    "Use two-step: transferOwnership + acceptOwnership"
                ]))
        return results

# 41: Symbol/decimals return bytes32 instead of string
class SymbolBytes32(AbstractDetector):
    ARGUMENT = "symbol-bytes32"
    HELP = "ERC20 symbol() returns bytes32 — incompatible with standard"
    IMPACT = DetectorClassification.LOW
    CONFIDENCE = DetectorClassification.LOW
    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:
                if f.name == 'symbol' and 'bytes32' in str(f.return_type):
                    results.append(self.generate_result([
                        f"Non-standard symbol: {c.name}",
                        "Returns bytes32 instead of string"
                    ]))
        return results

# 42: block.timestamp used for randomness
class TimestampRandom(AbstractDetector):
    ARGUMENT = "timestamp-random"
    HELP = "block.timestamp used as entropy source"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.HIGH
    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:
                src = f.source_code
                if 'block.timestamp' in src and any(k in f.name.lower() for k in ['random','draw','lottery','mint','roll']):
                    results.append(self.generate_result([
                        f"Timestamp as entropy: {f.name} in {c.name}",
                        "Use Chainlink VRF or commit-reveal scheme"
                    ]))
        return results

# 43: Missing zero address validation
class ZeroAddressCheck(AbstractDetector):
    ARGUMENT = "zero-address"
    HELP = "Address parameter not validated for address(0)"
    IMPACT = DetectorClassification.LOW
    CONFIDENCE = DetectorClassification.MEDIUM
    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            if not c.is_constructor: continue
            for f in [c.constructor] if hasattr(c,'constructor') else []:
                if f and 'address(0)' not in f.source_code and 'require' in f.source_code:
                    if any(p.type == 'address' for p in f.parameters):
                        results.append(self.generate_result([
                            f"Missing zero-address check: {c.name} constructor"
                        ]))
        return results

# 44: MEV Sandwich via no deadline/slippage
class MevSandwich(AbstractDetector):
    ARGUMENT = "mev-sandwich"
    HELP = "swap() without deadline enables sandwich attacks"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.MEDIUM
    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:
                if 'swap' not in f.name.lower() and 'trade' not in f.name.lower(): continue
                src = f.source_code
                if 'deadline' not in src and 'minOut' not in src and 'amountOutMin' not in src:
                    results.append(self.generate_result([
                        f"No deadline/slippage: {f.name} in {c.name}",
                        "Add deadline and minOut parameters"
                    ]))
        return results

# 45: Incorrect fallback accepting ETH
class IncorrectFallback(AbstractDetector):
    ARGUMENT = "incorrect-fallback"
    HELP = "Fallback silently accepts ETH — can lock funds"
    IMPACT = DetectorClassification.LOW
    CONFIDENCE = DetectorClassification.MEDIUM
    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:
                if not (f.is_fallback or f.is_receive): continue
                if 'revert' not in f.source_code:
                    results.append(self.generate_result([
                        f"ETH-accepting fallback: {c.name}",
                        "Consider reverting unexpected calls"
                    ]))
        return results

# 46: Missing event emission on state change
class MissingEvent(AbstractDetector):
    ARGUMENT = "missing-event"
    HELP = "State change without event — breaks off-chain tracking"
    IMPACT = DetectorClassification.LOW
    CONFIDENCE = DetectorClassification.LOW
    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:
                if 'view' in str(f.stateMutability) or 'pure' in str(f.stateMutability): continue
                if 'emit' not in f.source_code and f.visibility in ['public','external']:
                    if any(k in f.name for k in ['set','update','transfer','change']):
                        results.append(self.generate_result([
                            f"Missing event: {f.name} in {c.name}",
                            "Emit event for off-chain indexing"
                        ]))
        return results

# 47: tx.origin authentication
class TxOriginAuth(AbstractDetector):
    ARGUMENT = "tx-origin-auth"
    HELP = "tx.origin used for access control"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.HIGH
    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:
                if 'tx.origin' in f.source_code:
                    results.append(self.generate_result([
                        f"tx.origin auth: {f.name} in {c.name}",
                        "Use msg.sender instead of tx.origin"
                    ]))
        return results

# 48: Token decimals inconsistency
class DecimalsInconsistency(AbstractDetector):
    ARGUMENT = "decimals-inconsistency"
    HELP = "Using token decimals without normalization"
    IMPACT = DetectorClassification.LOW
    CONFIDENCE = DetectorClassification.LOW
    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:
                if 'decimals()' in f.source_code and '1e18' not in f.source_code and '10**' not in f.source_code:
                    results.append(self.generate_result([
                        f"Raw decimals: {f.name} in {c.name}",
                        "Normalize to 18 decimals for consistency"
                    ]))
        return results

# 49: Payable multicall with msg.value
class PayableMulticall(AbstractDetector):
    ARGUMENT = "payable-multicall"
    HELP = "multicall forwards msg.value — double-spend risk"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.MEDIUM
    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:
                if ('multicall' in f.name.lower() or 'batch' in f.name.lower()) and 'msg.value' in f.source_code:
                    results.append(self.generate_result([
                        f"Payable multicall: {f.name} in {c.name}",
                        "msg.value can be double-spent across calls"
                    ]))
        return results

# 50: Solidity version with known bugs
class SolidityVersionBugs(AbstractDetector):
    ARGUMENT = "solidity-version-bugs"
    HELP = "Using Solidity version with known vulnerabilities"
    IMPACT = DetectorClassification.LOW
    CONFIDENCE = DetectorClassification.HIGH
    def _detect(self):
        results = []
        risky = ['0.4','0.5','0.6','0.7']
        for c in self.compilation_unit.contracts_derived:
            ver = str(c.compilation_unit.pragma_directives[0][0]) if c.compilation_unit.pragma_directives else ''
            if any(v in ver for v in risky):
                if 'SafeMath' not in str(c.source_code) and '0.8' not in ver:
                    results.append(self.generate_result([
                        f"Risky Solidity version: {c.name} ({ver})",
                        "Pre-0.8 has no overflow protection; use SafeMath or upgrade"
                    ]))
        return results

"""
=== Slither Detectors Complete ===
50/50 detectors implemented
Coverage: 46/50 unique patterns (4 social/off-chain patterns excluded)
"""
