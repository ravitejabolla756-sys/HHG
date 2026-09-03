from app.utils.canonical_json import canonical_json
from app.utils.hashing import sha256_bytes
def test_canonical_json_and_hash():
    assert canonical_json({"b": 2, "a": 1}) == '{"a":1,"b":2}'
    assert sha256_bytes(canonical_json({"b": 2, "a": 1}).encode()) == "43258cff783fe7036d8a43033f830adfc60ec037382473548ac742b888292777"
