// Exercise: 闪贷费绕过
// Difficulty: ⭐⭐⭐
contract FlashLoan { function flashLoan(uint a) external returns (bool) { uint fee = a*3/1000; transfer(msg.sender, a); /* callback… */ require(repay > a+fee); /* ⚠️ What if repay == a+fee but in different token? */ }}