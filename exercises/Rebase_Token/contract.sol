// Exercise: Rebase代币通胀
// Difficulty: ⭐⭐⭐
contract VulnerableRebase { function rebase() external { totalSupply = totalSupply * index / prevIndex; /* ⚠️ No cap on rebase — extreme index changes cause overflow */ }}