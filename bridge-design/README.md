# Iron Bridge — Security-First Cross-Chain Bridge

## Design Philosophy

Every feature removed is a vulnerability prevented:
- ❌ No arbitrary calldata → prevents bridge hijacking
- ❌ No single-key admin → prevents key compromise
- ❌ No instant upgrades → users can exit before changes
- ❌ No trusted relayers → requires multi-sig guardian consensus

## Defense-in-Depth

| Layer | What It Prevents |
|:--:|------|
| 1. Structure | Malformed messages rejected before processing |
| 2. Replay | Double-spend impossible via nonce tracking |
| 3. Signatures | Unauthorized transfers require 4-of-7 guardians |
| 4. Rate Limit | Maximum 1,000 ETH/day → blast radius controlled |
| 5. Timelock | 48h before any upgrade → users can exit |
| 6. Pause | Emergency stop without drain capability |

## Formally Verifiable Invariants

All 6 invariants are designed to be provable with Certora: nonce uniqueness, rate limit, pause safety, supply conservation, upgrade timelock, guardian diversity.

## Built To Learn From

This bridge incorporates the lessons from:
- **Nomad $152M** → Defense-in-depth (Layer 1-4)
- **Ronin $625M** → Guardian diversity (4-of-7, not 5-of-9)
- **Uranium $50M** → Timelocked upgrades (48h)
- **PolyNetwork $610M** → No single admin key
- **Wormhole $326M** → Message format validation (Layer 1)
