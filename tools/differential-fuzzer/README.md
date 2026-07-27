# Differential EVM Fuzzer — Foundry (revm) vs geth

Compare Foundry's EVM implementation (revm) against geth's EVM.
Any divergence found affects every protocol tested with Foundry.

## Quick Start (WSL2/Linux)

```bash
# Install and start both nodes
bash setup.sh start

# In another terminal: run fuzzer
pip install web3 hexbytes
python differential_fuzzer.py 1000
```

## Architecture

```
Random bytecode → Deploy on revm (anvil) → Call → Compare gas/status/state
                → Deploy on geth (dev)   → Call → Compare gas/status/state
                                                    ↓
                                           Divergence → Report
```

## Known Divergences (to exclude)

- Gas metering: revm and geth use different gas models (revm is faster)
- Precompile addresses on non-mainnet chains
- Coinbase address differences in dev mode

## Impact

If a divergence is found, every Foundry test suite on Earth is potentially affected.
Foundry has 10,516 GitHub stars and is used by virtually every Solidity developer.

## References

- revm: https://github.com/bluealloy/revm
- geth: https://github.com/ethereum/go-ethereum
- Foundry: https://github.com/foundry-rs/foundry
