// Exercise 16: 授权前置
// Pattern: 授权前置 | Difficulty: ⭐⭐

// User: approve(spender, 1000)
// TX in mempool...
// Spender: transferFrom(user, spender, 1000) front-run
// Now approve: sets allowance to 1000
// Spender: transferFrom(user, spender, 1000) again — total 2000 spent!