// Certora Verification Language — 证明签名重放漏洞

rule noSignatureReplay(method f) {
    env e;
    address user;
    uint256 amount;
    bytes32 sourceTx;
    
    withdraw@withrevert(e, user, amount, sourceTx, 0);
    bool success1 = !lastReverted;
    
    withdraw@withrevert(e, user, amount, sourceTx, 0);
    bool success2 = !lastReverted;
    
    assert !(success1 && success2);
}
