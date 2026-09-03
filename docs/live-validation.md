# Live Polygon Amoy validation

Validated on 2026-09-03 against Polygon Amoy, chain ID `80002`.

## Deployment

- Contract: `VerificationRegistry`
- Address: `0xb44b993fFfA9EDEaD404Aa0B44fB639f3504B703`
- Deployment transaction: `0x045dfe48c792e4f1f4e7a4c13ffcf84566442e9a2e55501bac5d76d94f225615`
- Deployment block: `46634201`
- Contract explorer: <https://amoy.polygonscan.com/address/0xb44b993fFfA9EDEaD404Aa0B44fB639f3504B703>

## Historical pre-verification record

> **Not valid as matching evidence.** This record was created before Stage 5 compared the input face with provider-returned candidate thumbnails. It proves only that the listed payload was registered and read back correctly; it does not prove that the selected URL matched the input image. The immutable testnet record is retained here for transparent audit history and must not be used as final Task #3 evidence.

- Input image SHA-256: `dcb81b1c2315e6ac7fd0be8a671834347fc24cea272e5de1bcf6048ec5b8e718`
- Selected public result: <https://www.youtube.com/watch?v=uXTIgM-tS_s>
- Canonical payload SHA-256: `efb49a5068c2eda9c13b506cf9632d48b0b0fef2b9e2cd99ea2c1d35a035d618`
- On-chain event hash: `efb49a5068c2eda9c13b506cf9632d48b0b0fef2b9e2cd99ea2c1d35a035d618`
- Registration transaction: `0x42efb5aa38753797793acae4c795f00b6d125ed046ff82293b8f94588f52e365`
- Registration block: `46634265`
- Transaction explorer: <https://amoy.polygonscan.com/tx/0x42efb5aa38753797793acae4c795f00b6d125ed046ff82293b8f94588f52e365>
- Contract read-back: passed
- Local/event hash comparison: exact match

The transaction receipt status was `1`. A separate read-only process retrieved the record from `getVerification(bytes32)` and confirmed the source URL, platform, non-zero timestamp, submitting wallet, and emitted hash. That blockchain integrity check passed, but the old URL-selection logic did not verify visual identity. Raw images and face embeddings were not stored on-chain.

## Current fail-closed validation

On 2026-09-03, a fresh run with `examples/1100.png` returned 59 visual Lens matches, 0 exact matches, and 10 social-media candidates. Local InsightFace comparison rejected all 10 candidate thumbnails; the best cosine similarity was `0.1612`, below the required `0.45`. The command exited with code `1` before blockchain registration. No URL, payload, hash, or transaction from that run is represented as a successful match.
