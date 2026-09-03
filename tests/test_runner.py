from types import SimpleNamespace

import pytest

from app.face.detector import DetectedFace
from app.pipeline import runner
from app.reverse_search.client import SearchResponse
from app.reverse_search.parser import Candidate
from app.reverse_search.verifier import CandidateVerification, CandidateVerificationError


def test_unverified_candidates_never_reach_blockchain(monkeypatch):
    image = "unused-test-image.jpg"
    candidate = Candidate(
        "https://www.instagram.com/p/unrelated",
        "unrelated",
        "instagram",
        thumbnail_url="https://encrypted-tbn0.gstatic.com/unrelated",
    )
    evaluation = CandidateVerification(candidate, False, "face similarity", "below threshold", 0.1, 1)

    class Detector:
        def detect(self, _path):
            return [DetectedFace((0, 0, 1, 1), SimpleNamespace(embedding=[1.0, 0.0]))]

    class SearchClient:
        def __init__(self, _api_key):
            pass

        def search(self, _path):
            return SearchResponse(
                "SerpApi Google Lens",
                "ok",
                {"visual_matches": [{
                    "link": candidate.url,
                    "thumbnail": candidate.thumbnail_url,
                }]},
                1,
                0,
            )

    class Verifier:
        def __init__(self, _detector, _encoder):
            pass

        def select_match(self, _candidates, _embedding):
            raise CandidateVerificationError([evaluation])

    monkeypatch.setattr(runner, "FaceDetector", Detector)
    monkeypatch.setattr(runner, "ReverseSearchClient", SearchClient)
    monkeypatch.setattr(runner, "CandidateVerifier", Verifier)
    monkeypatch.setattr(runner, "sha256_file", lambda _path: "0" * 64)

    def unexpected_blockchain_call(*_args, **_kwargs):
        pytest.fail("blockchain subprocess must not run for an unverified candidate")

    monkeypatch.setattr(runner.subprocess, "run", unexpected_blockchain_call)
    settings = SimpleNamespace(validate=lambda: None, serpapi_api_key="configured", dry_run=False)

    with pytest.raises(CandidateVerificationError):
        runner.run(image, settings)
