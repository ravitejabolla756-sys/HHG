# Live Polygon Amoy validation

Validated against Polygon Amoy, chain ID `80002`. Deployment and historical evidence were first checked on 2026-09-03; the corrected post-fix pipeline was validated on 2026-09-06.

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

## Corrected post-fix verification record

This record was created only after the provider-returned Lens thumbnail passed local InsightFace comparison against the input face.

- Validation date: `2026-09-06`
- Input image SHA-256: `dcb81b1c2315e6ac7fd0be8a671834347fc24cea272e5de1bcf6048ec5b8e718`
- Lens visual matches: `59`
- Lens exact matches: `0`
- Parsed social candidates: `24`
- Candidate verification method: local InsightFace cosine similarity against the provider-returned Lens thumbnail
- Selected similarity: `0.8735`
- Required threshold: `0.45`
- Verified platform: `facebook`
- Verified public result: <https://www.facebook.com/groups/1626959317631302/posts/4476311472696058/>
- Canonical payload SHA-256: `9fd03140e8506ddd37e7743dd46976c61694eee0bbb125de8b50e3362212f7ce`
- On-chain event hash: `9fd03140e8506ddd37e7743dd46976c61694eee0bbb125de8b50e3362212f7ce`
- Registration transaction: `0x88818a992524bdf25a657d1e1519354ad22e402b45b924233048049db3517c71`
- Registration block: `46851898`
- Transaction explorer: <https://amoy.polygonscan.com/tx/0x88818a992524bdf25a657d1e1519354ad22e402b45b924233048049db3517c71>
- Transaction confirmed: `true`
- Local/on-chain hash match: `true`
- Independent contract read-back: `true`

The CLI printed `final verification result: PASS`. No source image, candidate thumbnail, or face embedding was persisted or registered.

## Post-fix fail-closed validation

On 2026-09-06, a fresh run with the approved local negative image returned 59 visual Lens matches, 0 exact matches, and 9 social-media candidates. Local InsightFace comparison rejected all 9 candidate thumbnails; the best cosine similarity was `0.1695`, below the required `0.45`. The command exited with code `1`, and Stage 6 never appeared, demonstrating that blockchain registration was not invoked. No URL, payload, hash, or transaction from that run is represented as a successful match.
