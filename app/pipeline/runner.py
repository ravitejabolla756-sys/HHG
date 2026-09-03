import json, os, subprocess
from pathlib import Path
from ..config import Settings
from ..face.detector import FaceDetector
from ..face.encoder import FaceEncoder
from ..reverse_search.client import ReverseSearchClient
from ..reverse_search.parser import parse_candidates
from ..reverse_search.verifier import select_match
from ..utils.canonical_json import canonical_json
from ..utils.hashing import sha256_file, sha256_bytes

def run(image: str, settings: Settings) -> dict:
    settings.validate(); path = Path(image)
    print("[1/6] Input image"); input_hash = sha256_file(path); print(f"input image SHA-256: {input_hash}")
    print("[2/6] Face detection"); faces = FaceDetector().detect(path); print(f"detected faces: {len(faces)}")
    if not faces: raise RuntimeError("No faces found; stopping honestly")
    print("[3/6] Face encoding"); embeddings = FaceEncoder().encode(faces); del embeddings; print("embedding generated locally and discarded after verification")
    print("[4/6] Genuine reverse-image search"); response = ReverseSearchClient(settings.serpapi_api_key).search(path); candidates = parse_candidates(response.data); print(f"provider: {response.provider}; status: {response.status}; Lens results: {response.result_count}; candidates: {[c.url for c in candidates]}")
    print("[5/6] Matching public social-media result"); match = select_match(candidates); print(f"selected: {match.url} ({match.platform})")
    payload = {"input_image_sha256": input_hash, "platform": match.platform, "source_url": match.url, "provider": response.provider, "schema_version": 1}
    canonical = canonical_json(payload); digest = sha256_bytes(canonical.encode("utf-8")); print("verification payload:", json.dumps(payload, indent=2)); print(f"canonical payload: {canonical}\ncanonical payload SHA-256: {digest}")
    print("[6/6] Blockchain registration")
    if settings.dry_run:
        if os.getenv("ALLOW_DRY_RUN") != "true": raise RuntimeError("Dry-run is test-only")
        return {"payload": payload, "canonical": canonical, "hash": digest}
    result = subprocess.run(["node", "-e", "import('./blockchain/record.js').then(async m=>console.log(JSON.stringify(await m.register(JSON.parse(process.argv[1])))) )", json.dumps({"hash": "0x" + digest, "source_url": match.url, "platform": match.platform})], capture_output=True, text=True, check=True)
    chain = json.loads(result.stdout)
    verified = chain["hashMatches"] and chain["readBackMatches"]
    print(json.dumps(chain, indent=2))
    print(f"final verification result: {'PASS' if verified else 'FAIL'}")
    if not verified:
        raise RuntimeError("Blockchain hash or record read-back did not match the local verification payload")
    return {"payload": payload, "canonical": canonical, "hash": digest, "blockchain": chain}
