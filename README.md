# Hacker House Goa 2026 — Task 3

## Face Identification + Reverse Image Search + Blockchain Verification

### Overview

This repository implements a CLI pipeline that checks whether a single-face input image has a visually corresponding result on a supported public social-media domain. It does not infer a person's legal identity or name from their face.

Face detection and embedding generation run locally with InsightFace. The embedding exists only in process memory and is retained only long enough to compare the input face with faces found in Google Lens result thumbnails.

The reverse-image-search boundary uses SerpApi's official Google Lens API with `engine=google_lens`, `type=all`, and `no_cache=true`. Social URLs are parsed dynamically from first-class Lens visual and exact matches; no expected URL, account, person, or search result is hardcoded.

Lens candidates are not trusted automatically. Each candidate must provide a usable thumbnail from a trusted Google/SerpApi image host, contain a detectable face, and meet the unchanged `0.45` cosine-similarity threshold. If every candidate is rejected, the CLI exits with code `1` before any blockchain call.

For a verified match, the application creates deterministic canonical JSON, calculates its SHA-256 digest, registers the digest and minimal public metadata through `VerificationRegistry` on Polygon Amoy, waits for confirmation, and independently reads the record back. Success requires both `hashMatches=true` and `readBackMatches=true`.

### Pipeline

```text
Input Image
   ↓
Local Face Detection
   ↓
Ephemeral Face Embedding
   ↓
SerpApi Google Lens
   ↓
Lens Social Candidates
   ↓
Local Face Similarity Verification
   ↓
Verified Public Social Result
   ↓
Canonical JSON
   ↓
SHA-256
   ↓
Polygon Amoy
   ↓
Independent Read-back
   ↓
PASS / REJECT
```

### Key Security / Privacy Properties

- Face detection and embedding comparison run locally.
- Embeddings are not logged, saved, cached, committed, or sent to the blockchain.
- Original and candidate images are not written to the blockchain.
- The chain receives only the deterministic hash, verified public source URL, platform, timestamp, and submitter address.
- Secrets are loaded from an ignored `.env` file.
- False, unavailable, faceless, and low-similarity candidates are rejected before registration.
- No social-media result is mocked, fabricated, preselected, or hardcoded.
- Deployment and writes refuse any chain other than Polygon Amoy (`80002`).

### Technologies

- Python 3.10+
- InsightFace with ONNX Runtime
- OpenCV and NumPy
- SerpApi Google Lens
- Node.js 20+
- ethers v6
- Hardhat
- Solidity 0.8.24
- Polygon Amoy
- SHA-256

### Requirements

- Python 3.10 or newer
- Node.js 20 or newer and npm
- SerpApi API key
- Polygon Amoy RPC endpoint
- Test-only wallet funded with Amoy POL
- Deployed `VerificationRegistry` contract
- JPG/JPEG, PNG, or WebP input no larger than 500 KB
- Exactly one detectable face in the input

### Installation

Run from Windows PowerShell:

```powershell
cd C:\HHG
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
npm install
Copy-Item .env.example .env
```

InsightFace downloads `buffalo_l` on first use into ignored `.models/insightface` storage.

### Environment Variables

Configure values locally in `.env`; never commit or display that file.

Required:

```text
SERPAPI_API_KEY
POLYGON_AMOY_RPC_URL
PRIVATE_KEY
CONTRACT_ADDRESS
CONTRACT_DEPLOYMENT_BLOCK
```

Optional/test-only:

```text
EXPLORER_BASE_URL
DRY_RUN
ALLOW_DRY_RUN
```

`DRY_RUN` is rejected unless `ALLOW_DRY_RUN=true`; it exists only for controlled tests and must not be used as live evidence.

### Contract Deployment

Deploy only when a new contract is actually required:

```powershell
npx hardhat compile
npx hardhat run scripts/deploy.js --network amoy
```

The deployment script verifies chain ID `80002` before writing. Copy the printed address and block number into `CONTRACT_ADDRESS` and `CONTRACT_DEPLOYMENT_BLOCK` in `.env`.

Current deployment:

- Network: Polygon Amoy
- Chain ID: `80002`
- Contract: [`0xb44b993fFfA9EDEaD404Aa0B44fB639f3504B703`](https://amoy.polygonscan.com/address/0xb44b993fFfA9EDEaD404Aa0B44fB639f3504B703)
- Deployment block: `46634201`

### Running the Pipeline

Use only an image you own, have consent to process, or that is clearly public and appropriate for this test:

```powershell
python -m app.main --image path\to\consented-image.jpg
```

The six stages are:

1. Validate the file and calculate its local SHA-256.
2. Require exactly one locally detected face.
3. Generate the ephemeral reference embedding.
4. Upload the image to SerpApi and request a fresh Google Lens response.
5. Parse social candidates, verify candidate-thumbnail faces locally, and select only a threshold-passing result.
6. Register the canonical-payload hash on Polygon Amoy, wait for confirmation, read back, and compare.

### Verification Logic

Google Lens inclusion alone is insufficient evidence. The parser accepts social URLs only from top-level `visual_matches` and `exact_matches`. For each candidate, the verifier retrieves the provider-returned thumbnail over HTTPS from an allowlisted Lens image host, limits the response size, decodes it in memory, and detects every visible face.

InsightFace embeddings from those faces are compared with the input embedding using cosine similarity. A candidate passes only when its best similarity is at least `0.45`; the highest verified score wins, with Lens match type and position used only as tie-breakers. A missing thumbnail, unsafe host, failed download, undecodable image, no face, incompatible embedding, or lower score is an explicit rejection.

If no candidate passes, the CLI prints the rejection evidence, reports no selected platform or URL, exits `1`, and never invokes the blockchain client. This verifies visual correspondence only—it is not legal identity, account ownership, or authorship proof.

### Blockchain

`VerificationRegistry` stores records keyed by the canonical payload's SHA-256:

- `sourceUrl`: verified public result URL
- `platform`: detected social platform
- `timestamp`: Amoy block timestamp
- `submitter`: testnet wallet address

The face image, thumbnail, embedding, SerpApi response, API credentials, and private key are never stored on-chain. The contract rejects duplicate hashes. The client safely handles a repeated payload by finding its original event, checking the confirmed receipt, reading the record independently, and returning the original transaction evidence.

### Testing

```powershell
python -m pytest -q
npm test
npm run test:blockchain
npx hardhat compile
```

The Python suite covers canonical hashing, parser boundaries, verified selection, low-similarity rejection, no-candidate rejection, untrusted thumbnail rejection, and proof that rejected candidates never invoke the blockchain subprocess. The Node test verifies the exact `bytes32` payload conversion. Hardhat compilation verifies the Solidity build.

### Negative Testing

- Missing image: file hashing fails and exits non-zero before provider access.
- Invalid image: OpenCV rejects unreadable image content.
- No face or multiple faces: Stage 2 exits before reverse search.
- False social candidate: local embedding comparison rejects it.
- Low similarity: a score below `0.45` is rejected.
- No verified result: Stage 6 is not reached and no transaction is submitted.
- Wrong network: deployment and blockchain writing reject any chain ID other than `80002`.

### Live Validation

See [docs/live-validation.md](docs/live-validation.md) for the deployed contract, immutable historical transaction evidence, and current post-fix validation status. Historical transactions created before candidate verification are labelled clearly and are not presented as proof of corrected matching.

### Known Limitations

- SerpApi and Google Lens availability, quotas, response formats, and coverage can change.
- Public posts and provider thumbnails can disappear or become inaccessible.
- Face similarity varies with quality, scale, crop, pose, lighting, age, and occlusion.
- The `0.45` threshold is a conservative project policy, not universal identity proof.
- A matching face does not establish account ownership, authorship, consent, or legal identity.
- Google Lens may return no usable social candidate even when related content exists publicly.
- Public-web metadata can be incomplete or incorrect.
- Polygon Amoy is a test network; RPC and explorer availability are not production guarantees.

More detail is available in [docs/limitations.md](docs/limitations.md).

### Privacy / Ethical Use

Run this pipeline only with the repository owner's image, an image of a person who has explicitly consented, or clearly public imagery where the use is appropriate. Do not use it for surveillance, harassment, doxxing, sensitive-trait inference, or claims of legal identity. Review every public result and its context before presenting it in a demonstration.

### Documentation

- [Architecture and trust boundaries](docs/architecture.md)
- [Live Polygon Amoy validation](docs/live-validation.md)
- [Unedited recording procedure](docs/demo-script.md)
- [Known limitations](docs/limitations.md)
- [Final submission checklist](FINAL_CHECKLIST.md)
