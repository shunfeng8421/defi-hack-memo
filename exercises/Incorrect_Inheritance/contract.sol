// Exercise: 错误的继承顺序
// Difficulty: ⭐⭐
contract A { uint a; } contract B is A { uint b; } contract C is A { uint c; } contract D is B, C { /* ⚠️ Diamond inheritance — which 'a' is used? */ }