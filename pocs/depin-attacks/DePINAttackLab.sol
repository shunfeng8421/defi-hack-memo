// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title DePIN Security Lab — 6 Decentralized Physical Infrastructure Attack Vectors
/// @notice Every "proof of physical work" can be faked. Here's how.
/// @author Shiqiang Chen · July 2026

// ============================================================
// #1: Location Spoofing (Helium/IoT)
// ============================================================
contract Attack1_LocationSpoofing {
    // Attack: Fake GPS coordinates to claim hotspot rewards
    // How: GPS signal can be spoofed with SDR (software-defined radio)
    // or simply by running multiple virtual hotspots at "different" locations
    
    // Helium: Proof-of-Coverage requires hotspots to "prove" they're at a location
    // Attack: 1 physical hotspot emulates 100 virtual hotspots
    // Each virtual hotspot claims different GPS coordinates → 100x rewards
    
    // Detection: Signal triangulation (need 3+ real hotspots to verify)
    // Fix: RSSI fingerprinting; time-of-flight verification
}

// ============================================================
// #2: Storage Proof Forgery (Filecoin/Arweave)
// ============================================================
contract Attack2_StorageForgery {
    // Attack: Claim you're storing data without actually storing it
    // Filecoin: Proof-of-Replication + Proof-of-Spacetime
    // Attack vectors:
    // 1. SNARK forgery: Build a fake proof faster than actual storage
    // 2. Multi-mining: Same storage unit claims credit for multiple files
    // 3. Replay: Store once, replay the proof for multiple blocks
    
    // Real risk: If generating proof < storing data, miners will cheat
    // Fix: Computation-to-storage ratio must make cheating unprofitable
}

// ============================================================
// #3: Bandwidth Inflation (Helium Mobile/5G)
// ============================================================
contract Attack3_BandwidthInflation {
    // Attack: Fake data transfer to claim bandwidth rewards
    // How: Two malicious nodes pretend to exchange data
    // Node A "sends" 1GB to Node B — but they just run a loop
    
    // Detection: Verify real user traffic
    // Fix: Require signed payment from unique end-users; not P2P loop
}

// ============================================================
// #4: IoT Sensor Data Manipulation
// ============================================================
contract Attack4_SensorManipulation {
    // Attack: Feed fake sensor data to weather/energy oracles
    // Example: WeatherXM — weather stations reporting on-chain
    // Attack: Put sensor in a freezer → report "snow in July"
    // Used to manipulate parametric insurance or energy trading
    
    // Fix: Multi-sensor consensus; outlier detection; ML anomaly detection
}

// ============================================================
// #5: Proof-of-Coverage Gaming (Wireless)
// ============================================================
contract Attack5_CoverageGaming {
    // Attack: Impersonate network coverage that doesn't exist
    // How: Deploy 1 high-power antenna → claims to cover 100km²
    // In reality: Signal propagates but no real users in that area
    
    // Economic attack: Claim rewards for "covered" areas with 0 real users
    // Fix: Tie rewards to ACTUAL user data transfer, not potential coverage
}

// ============================================================
// #6: Physical Sybil Attack
// ============================================================
contract Attack6_PhysicalSybil {
    // Attack: One physical device pretends to be N independent devices
    // Unlike digital Sybil (which costs 0), physical Sybil costs:
    // - Hardware cost per "virtual device"
    // - But specialized hardware can emulate many devices cheaply
    
    // Example: GPU rig with SDR → emulates 1000 IoT sensors
    // If reward per sensor > cost per virtual sensor → profitable attack
    
    // Fix: Trusted Execution Environment (TEE / SGX)
    // But: TEE itself can be attacked (side-channel, power glitching)
}

/// @title DePIN Summary
/// @dev Physical proofs are always weaker than cryptographic proofs
/// Key insight: The bridge between PHYSICAL world → DIGITAL verification
/// is always the attack surface.
