// Exercise: 代币税绕过
// Difficulty: ⭐⭐⭐
contract TokenWithTax { function transfer(address to, uint256 a) external returns (bool) { uint256 tax=0; if(!isExcluded[to]) tax = a*5/100; balance[to]+= a-tax; /* ⚠️ Exclusion list can be exploited */ }}