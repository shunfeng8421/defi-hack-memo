#!/usr/bin/env python3
"""
Differential EVM Fuzzer — Foundry (revm) vs geth EVM
Generates random EVM transactions, executes on both implementations,
and reports state divergence.
Author: Shiqiang Chen · July 2026
"""

import json, random, time, os, sys
from web3 import Web3
from hexbytes import HexBytes
from collections import defaultdict

# ============================================
# Configuration
# ============================================
REVM_RPC = "http://localhost:8545"   # anvil (revm)
GETH_RPC = "http://localhost:8546"   # geth dev mode

w3_revm = Web3(Web3.HTTPProvider(REVM_RPC))
w3_geth = Web3(Web3.HTTPProvider(GETH_RPC))

# ============================================
# Fuzzer Core
# ============================================
class DifferentialFuzzer:
    
    def __init__(self):
        self.iterations = 0
        self.divergences = []
        self.accounts = []
        
        if not w3_revm.is_connected():
            raise RuntimeError(f"Cannot connect to revm at {REVM_RPC}")
        if not w3_geth.is_connected():
            raise RuntimeError(f"Cannot connect to geth at {GETH_RPC}")
        
        # Create funded accounts
        for _ in range(10):
            acct = w3_revm.eth.account.create()
            # Fund on both chains
            for w3 in [w3_revm, w3_geth]:
                w3.eth.send_transaction({
                    'from': w3.eth.accounts[0],
                    'to': acct.address,
                    'value': w3.to_wei(100, 'ether')
                })
            self.accounts.append(acct)
        
        print(f"Connected. {len(self.accounts)} accounts funded.")
    
    def generate_random_bytecode(self) -> bytes:
        """Generate random EVM bytecode with basic validity."""
        opcodes = [
            # Stack ops
            '60',  # PUSH1
            '50',  # POP
            # Arithmetic
            '01', '02', '03', '04',  # ADD, MUL, SUB, DIV
            # Memory
            '51', '52',  # MLOAD, MSTORE
            '59',  # MSIZE
            # Storage
            '54', '55',  # SLOAD, SSTORE
            # Control flow
            '56', '57',  # JUMP, JUMPI
            '5b',  # JUMPDEST
            # Comparison
            '10', '11',  # LT, GT
            '14',  # EQ
            # Environment
            '33', '34',  # CALLER, CALLVALUE
            '38', '39',  # CODESIZE, CODECOPY
            '3a',  # GASPRICE
            # Return
            'f3',  # RETURN
            'fd',  # REVERT
            'ff',  # SELFDESTRUCT
            # Stop
            '00',  # STOP
        ]
        
        # Build random bytecode
        code = []
        for _ in range(random.randint(5, 50)):
            op = random.choice(opcodes)
            code.append(op)
            if op == '60':  # PUSH1 needs 1 byte
                code.append(format(random.randint(0, 255), '02x'))
        
        return bytes.fromhex(''.join(code))
    
    def deploy_and_call(self, bytecode: bytes) -> dict:
        """Deploy contract and call it on both EVMs."""
        # Build deploy tx
        deploy_tx = {
            'from': self.accounts[0].address,
            'gas': 1_000_000,
            'data': bytecode,
            'nonce': w3_revm.eth.get_transaction_count(self.accounts[0].address)
        }
        
        # Deploy on revm
        signed = w3_revm.eth.account.sign_transaction(deploy_tx, self.accounts[0].key)
        tx_hash_revm = w3_revm.eth.send_raw_transaction(signed.raw_transaction)
        receipt_revm = w3_revm.eth.wait_for_transaction_receipt(tx_hash_revm)
        contract_addr_revm = receipt_revm['contractAddress']
        
        # Deploy on geth (same nonce, same bytecode)
        deploy_tx_geth = dict(deploy_tx)
        deploy_tx_geth['nonce'] = w3_geth.eth.get_transaction_count(self.accounts[0].address)
        signed_geth = w3_geth.eth.account.sign_transaction(deploy_tx_geth, self.accounts[0].key)
        tx_hash_geth = w3_geth.eth.send_raw_transaction(signed_geth.raw_transaction)
        receipt_geth = w3_geth.eth.wait_for_transaction_receipt(tx_hash_geth)
        contract_addr_geth = receipt_geth['contractAddress']
        
        # Compare deployment
        divergence = {}
        
        if receipt_revm['status'] != receipt_geth['status']:
            divergence['deploy_status'] = {
                'revm': receipt_revm['status'],
                'geth': receipt_geth['status']
            }
        
        if receipt_revm['gasUsed'] != receipt_geth['gasUsed']:
            divergence['deploy_gas'] = {
                'revm': receipt_revm['gasUsed'],
                'geth': receipt_geth['gasUsed']
            }
        
        # Now send a random call to both contracts
        call_data = bytes.fromhex(
            format(random.choice([0x60, 0x00, 0x33, 0x38, 0x3a, 0x50]), '02x')
            + ''.join(format(random.randint(0,255), '02x') for _ in range(random.randint(0,10)))
        )
        
        call_tx = {
            'from': self.accounts[1].address,
            'to': contract_addr_revm,
            'gas': 500_000,
            'data': call_data,
        }
        
        # Call on revm
        call_tx['nonce'] = w3_revm.eth.get_transaction_count(self.accounts[1].address)
        signed_call = w3_revm.eth.account.sign_transaction(call_tx, self.accounts[1].key)
        call_hash_revm = w3_revm.eth.send_raw_transaction(signed_call.raw_transaction)
        call_receipt_revm = w3_revm.eth.wait_for_transaction_receipt(call_hash_revm)
        
        # Call on geth
        call_tx_geth = dict(call_tx)
        call_tx_geth['to'] = contract_addr_geth
        call_tx_geth['nonce'] = w3_geth.eth.get_transaction_count(self.accounts[1].address)
        signed_call_geth = w3_geth.eth.account.sign_transaction(call_tx_geth, self.accounts[1].key)
        call_hash_geth = w3_geth.eth.send_raw_transaction(signed_call_geth.raw_transaction)
        call_receipt_geth = w3_geth.eth.wait_for_transaction_receipt(call_hash_geth)
        
        if call_receipt_revm['status'] != call_receipt_geth['status']:
            divergence['call_status'] = {
                'revm': call_receipt_revm['status'],
                'geth': call_receipt_geth['status']
            }
        
        if call_receipt_revm['gasUsed'] != call_receipt_geth['gasUsed']:
            divergence['call_gas'] = {
                'revm': call_receipt_revm['gasUsed'],
                'geth': call_receipt_geth['gasUsed']
            }
        
        # Compare contract state
        revm_code = HexBytes(w3_revm.eth.get_code(contract_addr_revm)).hex()
        geth_code = HexBytes(w3_geth.eth.get_code(contract_addr_geth)).hex()
        if revm_code != geth_code:
            divergence['code'] = {
                'revm': revm_code[:50],
                'geth': geth_code[:50]
            }
        
        return divergence
    
    def run(self, iterations: int = 1000):
        print(f"Fuzzing {iterations} iterations...")
        start = time.time()
        
        for i in range(iterations):
            try:
                bytecode = self.generate_random_bytecode()
                divergence = self.deploy_and_call(bytecode)
                
                if divergence:
                    self.divergences.append({
                        'iteration': i,
                        'bytecode': bytecode.hex(),
                        'divergence': divergence
                    })
                    print(f"\n🔴 DIVERGENCE #{len(self.divergences)} at iteration {i}:")
                    for key, val in divergence.items():
                        print(f"   {key}: revm={val['revm']} vs geth={val['geth']}")
                
                if (i + 1) % 100 == 0:
                    elapsed = time.time() - start
                    rate = (i + 1) / elapsed
                    print(f"  [{i+1}/{iterations}] {rate:.0f} iter/s | {len(self.divergences)} divergences")
                    
            except Exception as e:
                continue  # Skip failed iterations
        
        print(f"\n{'='*60}")
        print(f"COMPLETE: {iterations} iterations in {time.time()-start:.1f}s")
        print(f"Divergences found: {len(self.divergences)}")
        
        if self.divergences:
            for d in self.divergences:
                print(f"\n  Iteration {d['iteration']}:")
                for key, val in d['divergence'].items():
                    print(f"    {key}: revm={val['revm']} vs geth={val['geth']}")
            
            # Save report
            with open("differential-fuzzer-report.json", "w") as f:
                json.dump(self.divergences, f, indent=2)
            print(f"\nReport saved to differential-fuzzer-report.json")
        
        return len(self.divergences)

# ============================================
# Entry point
# ============================================
if __name__ == "__main__":
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    
    try:
        fuzzer = DifferentialFuzzer()
        divergences = fuzzer.run(iterations)
        sys.exit(0 if divergences == 0 else 1)
    except RuntimeError as e:
        print(f"ERROR: {e}")
        print("Make sure both anvil (:8545) and geth (:8546) are running.")
        print("Run: bash setup.sh start")
        sys.exit(1)
