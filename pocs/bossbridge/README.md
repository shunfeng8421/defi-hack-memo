# BossBridge — Signature Replay
- Severity: 🔴 CRITICAL
- Pattern: #17 — Signature Replay
- Root: ECDSA signature lacks nonce and chainId
- Fix: Include nonce + chainId in signed message
- Real-world: Poly Network $610M
