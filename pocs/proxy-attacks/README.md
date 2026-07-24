# Proxy Attack Lab — 8 Vulnerability Patterns

80% of DeFi protocols use upgradeable proxies. 0% are systematically audited.

| # | Pattern | Severity | Real Case |
|:--:|------|:--:|------|
| 1 | UUPS Uninitialized Impl | 🔴 | — |
| 2 | Storage Collision | 🔴 | Compound migration |
| 3 | Transparent Selector Clash | 🟠 | — |
| 4 | Diamond Facet Override | 🟠 | — |
| 5 | Beacon Swap | 🟠 | — |
| 6 | Metamorphic CREATE2 | 🟡 | — |
| 7 | Self Delegatecall | 🟡 | — |
| 8 | Inherited Unprotected Init | 🔴 | Uranium $50M |
