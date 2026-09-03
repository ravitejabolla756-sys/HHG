# Hacker House Goa 2026 — Task 3

CLI-first, consent-only face encoding, genuine reverse-image search, and tamper-evident registration on Polygon Amoy.

## What it does

The pipeline detects every face locally with InsightFace `buffalo_l`, creates an ephemeral local embedding, sends the input image to a configured reverse-image-search provider, selects a provider-returned public social URL, builds a deterministic verification payload, hashes it with SHA-256, and registers only that hash plus minimal public metadata in `VerificationRegistry`. The model is downloaded on first use into the ignored `.models/insightface` directory.

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

The command prints all six stages, input hash, provider status and candidates, selected URL/platform, canonical payload and hash, transaction hash, explorer URL, and an independent read-back comparison. It fails with a non-zero exit code when no face or no real provider result is available.

Tests use `DRY_RUN=true` only through test fixtures; dry-run results are rejected unless `ALLOW_DRY_RUN=true` is explicitly set by the test process. Run the JavaScript payload test with `npm run test:blockchain`.

## Independent verification

Open the Amoy transaction URL printed by the CLI. Confirm the `VerificationRegistered` event, hash, source URL, timestamp, and submitting address. Recreate the exact canonical JSON printed by the CLI using sorted keys and compact separators, SHA-256 it, and compare it with the event hash. The CLI also calls the contract's public `getVerification` function after mining.

See [docs/architecture.md](docs/architecture.md), [docs/limitations.md](docs/limitations.md), and [docs/demo-script.md](docs/demo-script.md).

## Live Polygon Amoy evidence

The reference deployment and successful end-to-end registration are documented in [docs/live-validation.md](docs/live-validation.md). These are public testnet identifiers; no secrets or biometric data are included.
