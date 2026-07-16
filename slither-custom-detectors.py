"""
Slither 自定义检测器 — 移植 mcp-scan 方法论到区块链
检测: 瞬时价格预言机 (Flash-loan manipulable price)

安装:
  cp flash_price_oracle.py ~/.local/lib/python*/site-packages/slither/detectors/
  然后运行: slither . --detect flash-price-oracle
"""

from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.core.cfg.node import NodeType
from slither.slithir.operations import (InternalCall, HighLevelCall, 
                                         LibraryCall, Send, Transfer)

class FlashPriceOracle(AbstractDetector):
    ARGUMENT = "flash-price-oracle"
    HELP = "Detects flash-loan manipulable price oracle using AMM reserves"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.MEDIUM
    
    WIKI = "https://github.com/shunfeng8421/awesome-mcp-security"
    WIKI_TITLE = "Flash-loan manipulable price oracle"
    WIKI_DESCRIPTION = "Using AMM.getReserves() for price enables flash loan manipulation"
    WIKI_EXPLOIT_SCENARIO = """
    Attacker flash-loans tokens → swaps in AMM → manipulates reserves → exploits oracle.
    Use TWAP oracle instead: oracle.consult() not pool.getReserves().
    """
    WIKI_RECOMMENDATION = "Replace pool.getReserves() with a TWAP oracle"
    
    def _is_amm_reserve_call(self, ir):
        """Check if internal call is to getReserves()"""
        if isinstance(ir, (HighLevelCall, InternalCall, LibraryCall)):
            func_name = str(ir.function_name) if ir.function else ""
            return "getReserves" in func_name or "getReserve" in func_name
        return False
    
    def _detect(self):
        results = []
        
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                for node in function.nodes:
                    for ir in node.irs:
                        if self._is_amm_reserve_call(ir):
                            info = [
                                f"Flash-loan manipulable price in ",
                                f"{contract.name}.{function.name}()\n",
                                f"\t- Uses {ir.function_name}() at {node.source_mapping_str}\n",
                                f"\t- Replace with TWAP oracle\n",
                            ]
                            res = self.generate_result(info)
                            results.append(res)
                            break  # One warning per function
        return results

# ============================================
# 更多检测器可以加在这里
# ============================================

class UncheckedTransfer(AbstractDetector):
    ARGUMENT = "unchecked-transfer-erc20"
    HELP = "Detects ERC20 transfer without return value check"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.HIGH
    
    def _detect(self):
        results = []
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                for node in function.nodes:
                    for ir in node.irs:
                        if isinstance(ir, (HighLevelCall, InternalCall)):
                            func_name = str(ir.function_name) if ir.function else ""
                            if func_name in ("transfer", "transferFrom"):
                                # Check if return value is used
                                if not ir.lvalue:
                                    info = [
                                        f"Unchecked ERC20 transfer in ",
                                        f"{contract.name}.{function.name}()\n",
                                        f"\t- {ir.function_name}() return value not checked\n",
                                        f"\t- Use SafeERC20.safeTransfer()\n",
                                    ]
                                    res = self.generate_result(info)
                                    results.append(res)
        return results
