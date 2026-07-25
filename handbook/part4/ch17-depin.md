# Chapter 17: DePIN Physical-Layer Attacks

*"Every proof of physical work can be faked. The question is: at what cost?"*

---

## The Helium Location Spoofing Dilemma

Helium is a decentralized wireless network where hotspot operators earn HNT tokens for providing network coverage. Hotspots prove their coverage through "Proof-of-Coverage"—a challenge-response mechanism where one hotspot challenges another to prove it can hear the signal.

The problem: GPS coordinates are self-reported. A hotspot operator using software-defined radio can spoof GPS signals, making one physical hotspot appear to be 100 virtual hotspots at 100 different locations, each earning full rewards.

Helium addressed this through RSSI fingerprinting—measuring signal strength patterns that vary with distance—and through "witness" hotspots that verify challenges. But the fundamental tension remains: **physical truth must be translated into digital proof, and the translation layer is the attack surface.**

---

## DePIN Attack Classes

Decentralized Physical Infrastructure Networks span wireless (Helium), storage (Filecoin, Arweave), compute (Render Network), and sensor data (WeatherXM). Each has a unique attack surface, but they share a common vulnerability: **the oracle problem applied to hardware.**

---

## Pattern #45: Location Spoofing (GPS/SDR)

**Severity**: HIGH
**Target**: Helium, Hivemapper, DIMO

### The Attack

GPS signals can be spoofed using a Software-Defined Radio (SDR) costing under $300. The SDR transmits fake GPS signals that override the receiver's real position. To the on-chain contract, the hotspot appears to be exactly where the operator claims.

### The Fix

Multi-modal location verification: combine GPS with cell tower triangulation, WiFi fingerprinting, and neighbor voting. One modality can be spoofed. All four cannot.

---

## Pattern #46: Storage Proof Forgery

**Severity**: CRITICAL
**Target**: Filecoin, Arweave, Storj

### The Attack

Filecoin miners must prove they are storing specific data. The proof mechanism (Proof-of-Replication + Proof-of-Spacetime) requires computationally expensive SNARK generation that is intentionally slower than the storage operation.

But: if generating the proof becomes faster than actually storing the data, miners will generate proofs without storing anything. The attack is economic: the proof cost must always exceed the storage cost.

### The Fix

Computation-to-storage ratio monitoring. If proof generation time drops below the storage write time for the same data size, increase proof difficulty.

---

## The DePIN Checklist

1. **Physical proof mechanisms must be more expensive to fake than to perform honestly.**
2. **Multiple independent verification modalities for every physical claim.**
3. **Rewards are tied to verified usage, not self-reported coverage.**

---

*Next: Chapter 18 — ZK Circuit Vulnerabilities*
