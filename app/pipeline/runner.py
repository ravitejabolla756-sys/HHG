import json
import os
from pathlib import Path
import subprocess

from ..config import Settings
from ..face.detector import FaceDetector
from ..face.encoder import FaceEncoder
from ..reverse_search.client import ReverseSearchClient
from ..reverse_search.parser import parse_candidates
from ..reverse_search.verifier import CandidateVerificationError, CandidateVerifier
from ..utils.canonical_json import canonical_json
from ..utils.hashing import sha256_bytes, sha256_file


def _print_evaluations(evaluations) -> None:
    rejected = [item for item in evaluations if not item.verified]
    print(f"Lens social candidates found: {len(evaluations)}")
    print(f"candidates rejected as non-matches: {len(rejected)}")
    for item in rejected:
        print(f"  REJECTED [{item.candidate.platform}] {item.candidate.url} - {item.evidence}")


def run(image: str, settings: Settings) -> dict:
    settings.validate()
    path = Path(image)
    print("[1/6] Input image")
    input_hash = sha256_file(path)
    print(f"input image SHA-256: {input_hash}")

    detector = FaceDetector()
    encoder = FaceEncoder()
    print("[2/6] Face detection")
    faces = detector.detect(path)
    print(f"detected faces: {len(faces)}")
    if len(faces) != 1:
        raise RuntimeError(f"Expected exactly one input face, found {len(faces)}; stopping honestly")

    print("[3/6] Face encoding")
    reference_embedding = encoder.encode(faces)[0]
    del faces
    print("embedding generated locally; retained only in process memory for candidate verification")

    print("[4/6] Genuine reverse-image search")
    response = ReverseSearchClient(settings.serpapi_api_key).search(path)
    candidates = parse_candidates(response.data)
    print(
        f"provider: {response.provider}; status: {response.status}; "
        f"visual matches: {response.visual_match_count}; exact matches: {response.exact_match_count}"
    )

    print("[5/6] Evidence-based social-media candidate verification")
    verifier = CandidateVerifier(detector, encoder)
    try:
        selection = verifier.select_match(candidates, reference_embedding)
    except CandidateVerificationError as exc:
        _print_evaluations(exc.evaluations)
        print("verified matching candidate: NONE")
        print("platform: NONE")
        print("source URL: NONE")
        print("verification method: InsightFace cosine similarity against provider-returned Lens thumbnails")
        print("verification evidence: no candidate met the required face-similarity threshold")
        raise
    finally:
        del reference_embedding
    _print_evaluations(selection.evaluations)
    match = selection.match
    print(f"verified matching candidate: {match.url}")
    print(f"platform: {match.platform}")
    print(f"source URL: {match.url}")
    print(f"verification method: {selection.evidence.method}")
    print(f"verification evidence: {selection.evidence.evidence}; Lens match type: {match.match_type}")
    print("input and candidate face embeddings discarded; no embedding persisted")

    payload = {
        "input_image_sha256": input_hash,
        "platform": match.platform,
        "source_url": match.url,
        "provider": response.provider,
        "schema_version": 1,
    }
    canonical = canonical_json(payload)
    digest = sha256_bytes(canonical.encode("utf-8"))
    print("verification payload:", json.dumps(payload, indent=2))
    print(f"canonical payload: {canonical}\ncanonical payload SHA-256: {digest}")

    print("[6/6] Blockchain registration")
    if settings.dry_run:
        if os.getenv("ALLOW_DRY_RUN") != "true":
            raise RuntimeError("Dry-run is test-only")
        return {"payload": payload, "canonical": canonical, "hash": digest}
    result = subprocess.run(
        [
            "node",
            "-e",
            "import('./blockchain/record.js').then(async m=>console.log(JSON.stringify(await m.register(JSON.parse(process.argv[1])))) )",
            json.dumps({"hash": "0x" + digest, "source_url": match.url, "platform": match.platform}),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    chain = json.loads(result.stdout)
    verified = chain["hashMatches"] and chain["readBackMatches"]
    print(json.dumps(chain, indent=2))
    print(f"final verification result: {'PASS' if verified else 'FAIL'}")
    if not verified:
        raise RuntimeError("Blockchain hash or record read-back did not match the local verification payload")
    return {"payload": payload, "canonical": canonical, "hash": digest, "blockchain": chain}
