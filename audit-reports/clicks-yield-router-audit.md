# ClicksYieldRouter — AI Agent × DeFi Security Audit

**Auditor**: Shiqiang Chen | **Date**: July 18, 2026  
**Project**: Clicks Protocol | **Contract**: ClicksYieldRouter.sol (426 lines)

## Executive Summary

| # | Finding | Severity | AI Attack Vector |
|:--:|------|:--:|------|
| 1 | No ReentrancyGuard on deposit/withdraw | 🟠 HIGH | Vector #2: Auto-DeFi Chain |
| 2 | Live APY routing can be gamed | 🟡 MEDIUM | Vector #3: Oracle Poisoning |
| 3 | Single splitter = SPOF for AI Agent | 🟡 MEDIUM | Vector #8: Signing Theft |
| 4 | Unchecked assembly return values | 🔵 LOW | — |

## Finding 1: Missing ReentrancyGuard

**Lines**: 124-162 (deposit), 169-236 (withdraw)

### Description
Both `deposit()` and `withdraw()` make external calls to Aave/Morpho without `nonReentrant` protection. While CEI pattern is followed, the Aave/Morpho ERC-4626-like tokens have hooks that could reenter.

### AI Agent Impact
If an AI agent deposits via the splitter and the Aave aUSDC token triggers a callback:
→ Agent's deposit accounting is already updated → but external call can still exploit
→ If agent uses a malicious aUSDC clone → reentrancy → drain

### Fix
```solidity
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
contract ClicksYieldRouter is Ownable, ReentrancyGuard {
    function deposit(uint256 amount, address agent) external onlySplitter nonReentrant {
```

---

## Finding 2: Real-Time APY Routing Can Be Manipulated

**Lines**: 132, 244-269

### Description
`_getBestProtocol()` compares live `getAaveAPY()` and `getMorphoAPY()` on every deposit. Morpho APY is approximated from `totalBorrow / totalSupply` which can change in a single transaction.

### Attack Scenario
1. AI Agent monitors APY → sees Morpho > Aave → deposits
2. Attacker front-runs: deposits into Morpho → utilization drops → APY drops
3. AI Agent's deposit now goes to Morpho at lower actual rate
4. Attacker withdraws → AI funds stuck at suboptimal rate

### AI Agent Impact
AI agent's "automatic routing" decision is based on manipulable on-chain data. Agent has no way to distinguish a real APY change from manipulation.

### Fix
```solidity
// Add minimum observation window for APY changes
uint256 public lastAPYUpdate;
uint256 public constant APY_STALENESS = 1 hours;
function _getBestProtocol() internal view returns (uint8) {
    require(block.timestamp - lastAPYUpdate >= APY_STALENESS, "APY too fresh");
    // ... existing logic
}
```

---

## Finding 3: Splitter as Single Point of AI Agent Failure

**Lines**: 47, 78-81

### Description
The `splitter` address has full control over all agent funds. If the AI agent controlling the splitter is:
- Prompt-injected → attacker gains full access
- Algorithmically confused → accidental drain
- Crashed → funds permanently locked

### AI Agent Impact
This is the **exact attack vector #8** from our taxonomy. The AI agent holds signing authority but has no built-in safety constraints: no per-agent limits, no delay, no multi-sig.

### Fix
Add per-agent withdrawal limits and a timelock for splitter changes.

---

*Report filed under: AI Agent × DeFi Security Research | shunfeng8421/defi-hack-memo*
