# Hacker House Goa 2026 — Task 3

CLI-first, consent-only face encoding, genuine reverse-image search, and tamper-evident registration on Polygon Amoy.

## What it does

The pipeline requires exactly one input face, creates an ephemeral local InsightFace `buffalo_l` embedding, and sends the input image to the configured reverse-image-search provider. Social URLs are parsed only from first-class Lens visual/exact matches. Each candidate must then pass a local face-embedding comparison against its provider-returned Lens thumbnail before selection. Unverified URLs are rejected, and an empty verified set stops the process before blockchain registration. A verified result is recorded as deterministic canonical JSON whose SHA-256 and minimal public metadata are registered in `VerificationRegistry`. The model is downloaded on first use into the ignored `.models/insightface` directory.

No face image, embedding, private profile data, or biometric data is written to the chain. Use only an image of the repository owner, a consenting person, or a clearly public image.

## Setup

Requirements: Python 3.10+, Node.js 20+, an Amoy-funded wallet, a deployed contract, and a configured reverse-image provider. Supply a consented image path at runtime; no biometric sample is committed to this repository.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm install
Copy-Item .env.example .env
```

Set `SERPAPI_API_KEY`, `POLYGON_AMOY_RPC_URL`, `PRIVATE_KEY`, and `CONTRACT_ADDRESS` in `.env`. The provider adapter uploads the local image to SerpApi's official Image API, then calls the Google Lens Search API with `engine=google_lens`, `type=all`, and `no_cache=true`. The upload must be JPG/JPEG, PNG, or WebP and no larger than 500 KB.

## Contract deployment

```powershell
npx hardhat compile
npx hardhat run scripts/deploy.js --network amoy
```

Copy the printed address and deployment block into `CONTRACT_ADDRESS` and `CONTRACT_DEPLOYMENT_BLOCK`. The block is used for provider-compatible event lookup when verifying an existing record. Never commit `.env` or private keys.

## Run

```powershell
python -m app.main --image path\to\consented-image.jpg
```

The command prints all six stages, input hash, provider status, Lens visual/exact counts, rejected candidates, the verified URL/platform and verification evidence, canonical payload and hash, transaction hash, explorer URL, and an independent read-back comparison. Candidate verification uses cosine similarity between the input face embedding and faces detected in trusted provider-returned Lens thumbnails, with a conservative `0.45` acceptance threshold. Embeddings and thumbnails remain in process memory and are discarded. The command exits non-zero before blockchain registration when the image does not contain exactly one face or no social candidate can be verified.

Tests use `DRY_RUN=true` only through test fixtures; dry-run results are rejected unless `ALLOW_DRY_RUN=true` is explicitly set by the test process. Run the JavaScript payload test with `npm run test:blockchain`.

## Independent verification

Open the Amoy transaction URL printed by the CLI. Confirm the `VerificationRegistered` event, hash, source URL, timestamp, and submitting address. Recreate the exact canonical JSON printed by the CLI using sorted keys and compact separators, SHA-256 it, and compare it with the event hash. The CLI also calls the contract's public `getVerification` function after mining.

See [docs/architecture.md](docs/architecture.md), [docs/limitations.md](docs/limitations.md), and [docs/demo-script.md](docs/demo-script.md).

## Live Polygon Amoy evidence

The reference contract deployment and historical pre-verification registration are documented in [docs/live-validation.md](docs/live-validation.md). Historical records created before candidate face verification was added must not be treated as verified matching evidence. A submission-quality live run requires Stage 5 to print a verified candidate and Stage 6 to confirm its resulting hash on-chain. These are public testnet identifiers; no secrets or biometric data are included.
