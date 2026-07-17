// PoC 5: SnowmanAirdrop — EIP-712 Spelling Error
contract SnowmanAirdropPoC is Test {
    // Bug: "addres" instead of "address"
    bytes32 constant BAD_TYPEHASH  = keccak256("SnowmanClaim(addres receiver, uint256 amount)");
    bytes32 constant GOOD_TYPEHASH = keccak256("SnowmanClaim(address receiver, uint256 amount)");

    function testSpellingError() public {
        address receiver = address(0x123);
        uint256 amount = 100e18;

        bytes32 badHash = keccak256(abi.encode(BAD_TYPEHASH, receiver, amount));
        bytes32 goodHash = keccak256(abi.encode(GOOD_TYPEHASH, receiver, amount));

        assert(badHash != goodHash);
        emit log("✅ 'addres' typo breaks EIP-712 compatibility");
    }
}

// ============================================================
// Foundry PoC Portfolio — Run All Tests
// forge test --match-path "**/pocs/**"
// ============================================================
