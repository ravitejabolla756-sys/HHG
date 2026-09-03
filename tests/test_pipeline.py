import pytest
from types import SimpleNamespace

from app.face.detector import DetectedFace
from app.face.encoder import FaceEncoder
from app.reverse_search.parser import parse_candidates
from app.reverse_search.client import SearchResponse
from app.reverse_search.verifier import CandidateVerificationError, CandidateVerifier


def test_parser_extracts_only_real_social_urls():
    result = parse_candidates({
        "visual_matches": [{
            "position": 2,
            "link": "https://www.instagram.com/p/visual",
            "title": "visual",
            "source": "Instagram",
            "thumbnail": "https://encrypted-tbn0.gstatic.com/image-a",
        }],
        "exact_matches": [{
            "position": 1,
            "link": "https://m.tiktok.com/v/exact",
            "title": "exact",
            "thumbnail": "https://encrypted-tbn0.gstatic.com/image-b",
        }],
        "organic_results": [{"link": "https://www.facebook.com/not-a-lens-match"}],
    })
    assert [x.platform for x in result] == ["tiktok", "instagram"]
    assert result[0].match_type == "exact"
    assert result[1].thumbnail_url == "https://encrypted-tbn0.gstatic.com/image-a"


class StubDetector:
    def detect_array(self, image):
        return [DetectedFace((0, 0, 1, 1), SimpleNamespace(embedding=image))]


def _candidate_payload():
    return parse_candidates({
        "visual_matches": [
            {"link": "https://www.instagram.com/p/unrelated", "thumbnail": "https://encrypted-tbn0.gstatic.com/unrelated"},
            {"link": "https://www.youtube.com/watch?v=related", "thumbnail": "https://encrypted-tbn0.gstatic.com/related"},
        ]
    })


def test_verifier_rejects_unrelated_face_and_selects_related_face():
    verifier = CandidateVerifier(StubDetector(), FaceEncoder(), threshold=0.8)
    vectors = {
        "https://encrypted-tbn0.gstatic.com/unrelated": [0.0, 1.0],
        "https://encrypted-tbn0.gstatic.com/related": [0.99, 0.01],
    }
    verifier._download_thumbnail = lambda url: vectors[url]

    selection = verifier.select_match(_candidate_payload(), [1.0, 0.0])

    assert selection.match.platform == "youtube"
    assert selection.evidence.verified is True
    assert selection.evaluations[0].verified is False


def test_no_verified_match_fails_closed():
    verifier = CandidateVerifier(StubDetector(), FaceEncoder(), threshold=0.8)
    verifier._download_thumbnail = lambda _url: [0.0, 1.0]

    with pytest.raises(CandidateVerificationError) as exc_info:
        verifier.select_match(_candidate_payload(), [1.0, 0.0])

    assert len(exc_info.value.evaluations) == 2
    assert all(not item.verified for item in exc_info.value.evaluations)


def test_no_candidates_fails_closed():
    verifier = CandidateVerifier(StubDetector(), FaceEncoder())
    with pytest.raises(CandidateVerificationError) as exc_info:
        verifier.select_match([], [1.0, 0.0])
    assert exc_info.value.evaluations == []


def test_untrusted_thumbnail_host_is_rejected():
    with pytest.raises(RuntimeError, match="trusted Lens image host"):
        CandidateVerifier._validate_thumbnail_url("https://example.com/image.jpg")

def test_lens_result_count_combines_visual_and_exact_matches():
    response = SearchResponse("SerpApi Google Lens", "ok", {}, 3, 2)
    assert response.result_count == 5
