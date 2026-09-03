import pytest
from app.reverse_search.parser import parse_candidates
from app.reverse_search.verifier import select_match
from app.reverse_search.client import SearchResponse
def test_parser_extracts_only_real_social_urls():
    result = parse_candidates({
        "visual_matches": [{"link": "https://www.instagram.com/p/visual", "title": "visual"}],
        "exact_matches": [{"link": "https://m.tiktok.com/v/exact", "title": "exact"}],
        "organic_results": [{"link": "https://example.com/not-social"}],
    })
    assert [x.platform for x in result] == ["instagram", "tiktok"]
def test_no_match_fails():
    with pytest.raises(RuntimeError): select_match([])

def test_lens_result_count_combines_visual_and_exact_matches():
    response = SearchResponse("SerpApi Google Lens", "ok", {}, 3, 2)
    assert response.result_count == 5
