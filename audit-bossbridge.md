# BossBridge — Signature Replay Vulnerability

**Source**: Cyfrin First Flight #4 | **Severity**: 🔴 CRITICAL

---

## Description

The `withdrawTokensToL1` function uses ECDSA signatures without including a nonce, chain ID, or any replay protection. Once a signer authorizes a withdrawal, the same signature can be replayed indefinitely to drain the vault.

## Vulnerability

```solidity
// L1BossBridge.sol:112-125
function sendToL1(uint8 v, bytes32 r, bytes32 s, bytes memory message) 
    public nonReentrant whenNotPaused 
{
    address signer = ECDSA.recover(
        MessageHashUtils.toEthSignedMessageHash(keccak256(message)), v, r, s
    );
    if (!signers[signer]) revert Unauthorized();
    
    (address target, uint256 value, bytes memory data) = 
        abi.decode(message, (address, uint256, bytes));
    (bool success,) = target.call{value: value}(data);
}
```

Three issues:
1. **No nonce** — same message can be replayed forever
2. **No chain ID** — signature valid on all chains
3. **`sendToL1` is public** — anyone can call with any valid message

## Attack

```
1. Signer authorizes: withdrawTokensToL1(alice, 1000, sig)
   → message encodes transferFrom(vault, alice, 1000)
2. Alice withdraws 1000 tokens (legitimate)
3. Attacker replays same signature → withdraws another 1000
4. Repeats until vault is empty
```

## Fix

```solidity
// Add nonce + chain ID
mapping(address => uint256) public nonces;

function sendToL1(...) {
    bytes32 hash = keccak256(abi.encodePacked(
        message, nonces[signer]++, block.chainid
    ));
    address signer = ECDSA.recover(
        MessageHashUtils.toEthSignedMessageHash(hash), v, r, s
    );
}
```

## Pattern Match
**DeFi Pattern #27**: Signature Replay — same as PolyNetwork $610M and NomadBridge $152M.
