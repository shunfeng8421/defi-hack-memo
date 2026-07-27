#!/bin/bash
# Differential EVM Fuzzer — Setup & Run
# Compares Foundry's revm against geth's EVM for implementation divergence
# Author: Shiqiang Chen · July 2026

set -e

echo "=== Differential EVM Fuzzer ==="
echo "Comparing Foundry (revm) vs geth EVM"
echo ""

# ============================================
# Step 1: Install dependencies
# ============================================
install_deps() {
    echo "[1/4] Installing Foundry..."
    if ! command -v anvil &>/dev/null; then
        curl -L https://foundry.paradigm.xyz | bash
        foundryup
    fi
    
    echo "[2/4] Installing geth..."
    if ! command -v geth &>/dev/null; then
        sudo add-apt-repository -y ppa:ethereum/ethereum
        sudo apt-get update
        sudo apt-get install -y ethereum
    fi
    
    echo "[3/4] Installing Python deps..."
    pip install web3 hexbytes 2>/dev/null
    
    echo "[4/4] Creating dev chains..."
}

# ============================================
# Step 2: Start both EVMs
# ============================================
start_nodes() {
    echo "Starting anvil (revm) on :8545..."
    anvil --port 8545 --chain-id 1337 &
    ANVIL_PID=$!
    sleep 2
    
    echo "Starting geth dev mode on :8546..."
    TMPDIR=$(mktemp -d)
    geth --dev --http --http.port 8546 --http.api eth,debug \
         --datadir "$TMPDIR" --dev.period 0 &
    GETH_PID=$!
    sleep 3
    
    echo "anvil PID: $ANVIL_PID | geth PID: $GETH_PID"
}

# ============================================
# Step 3: Run the fuzzer
# ============================================
run_fuzzer() {
    echo "Starting fuzzer..."
    python3 differential_fuzzer.py "$@"
}

# ============================================
# Step 4: Cleanup
# ============================================
cleanup() {
    echo "Stopping nodes..."
    kill $ANVIL_PID 2>/dev/null
    kill $GETH_PID 2>/dev/null
    echo "Done."
}
trap cleanup EXIT

# ============================================
# Main
# ============================================
case "${1:-run}" in
    install)
        install_deps
        ;;
    start)
        install_deps
        start_nodes
        echo "Nodes running. Press Ctrl+C to stop."
        wait
        ;;
    run)
        install_deps
        start_nodes
        run_fuzzer "${@:2}"
        ;;
    *)
        echo "Usage: $0 {install|start|run [iterations]}"
        ;;
esac
