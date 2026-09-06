# Unedited demo procedure

Use two explicitly approved local images:

- **Positive image:** a consenting/public image already confirmed to produce a verified social candidate at similarity `>= 0.45`.
- **Negative image:** a consenting/public image whose Lens social candidates are unrelated or below `0.45`.

Both images must remain ignored by Git. Do not open `.env`, browser developer tools containing request credentials, wallet settings, or terminal history that could reveal secrets.

## Recording preparation

1. Open the repository root and show the source folders, README, contract, tests, and documentation.
2. Show `.env.example` to demonstrate variable names only.
3. Run `git status --short --branch` and `git check-ignore .env path\to\positive-image.jpg`.
4. Open the public Polygon Amoy contract page linked from the README.
5. Clear the terminal. Keep the recording continuous from the pipeline command through final verification.

## Positive flow

1. Run:

   ```powershell
   python -m app.main --image path\to\approved-positive-image.jpg
   ```

2. Show Stage 1 validating the image and calculating its input SHA-256.
3. Show Stage 2 detecting exactly one face.
4. Show Stage 3 generating the local ephemeral embedding without printing it.
5. Show Stage 4 reporting `SerpApi Google Lens`, request success, and fresh visual/exact counts.
6. Show Stage 5 listing Lens social candidates and explicit rejection evidence.
7. Show the verified candidate, platform, public source URL, verification method, similarity score, and unchanged `0.45` threshold.
8. Show the deterministic verification payload, compact canonical JSON, and SHA-256.
9. Show Stage 6 using Polygon Amoy chain ID `80002`.
10. Show the confirmed transaction hash, block number, contract address, and explorer URL.
11. Show `hashMatches: true`.
12. Show `readBackMatches: true` and `final verification result: PASS`.
13. Open the printed transaction URL and show the confirmed `VerificationRegistered` event without exposing wallet secrets.

## Negative flow

1. Run:

   ```powershell
   python -m app.main --image path\to\approved-negative-image.jpg
   ```

2. Show genuine fresh Lens counts and the returned social candidates.
3. Show that each false/low-similarity candidate is marked `REJECTED` with evidence.
4. Show `verified matching candidate: NONE` and the non-zero exit.
5. Point out that `[6/6] Blockchain registration` never appears, proving no transaction was attempted.

## Recording acceptance checklist

- One continuous successful pipeline execution is visible.
- A real provider response and dynamic candidate verification are visible.
- The selected social URL is manually inspected and visibly corresponds to the input image.
- Canonical payload, SHA-256, transaction, and independent read-back are visible.
- The negative run visibly stops before blockchain registration.
- No secret, private image file content beyond the approved demo images, or embedding is exposed.
