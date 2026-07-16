// Exercise: 贷款创建竞态
// Difficulty: ⭐⭐⭐
contract VulnerableLoan { function takeLoan(uint a) external { require(collateral[msg.sender]*price >= a*LTV); borrows[msg.sender] += a; /* ⚠️ Price checked BEFORE collateral deposited — flash loan attack */ }}