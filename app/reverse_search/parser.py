from dataclasses import dataclass
from urllib.parse import urlparse


SOCIAL_DOMAINS = {
    "instagram.com": "instagram",
    "tiktok.com": "tiktok",
    "x.com": "x",
    "twitter.com": "x",
    "facebook.com": "facebook",
    "youtube.com": "youtube",
    "threads.net": "threads",
    "linkedin.com": "linkedin",
}


@dataclass(frozen=True)
class Candidate:
    url: str
    title: str
    platform: str
    match_type: str = "visual"
    position: int | None = None
    source: str = ""
    thumbnail_url: str | None = None

def _platform_for_host(host: str) -> str | None:
    for domain, platform in SOCIAL_DOMAINS.items():
        if host == domain or host.endswith("." + domain):
            return platform
    return None


def _thumbnail_url(item: dict) -> str | None:
    for key in ("thumbnail", "image", "image_url"):
        value = item.get(key)
        if isinstance(value, str) and value.startswith(("https://", "http://")):
            return value
    return None


def parse_candidates(payload: dict) -> list[Candidate]:
    """Parse only first-class Lens matches, never arbitrary nested URLs."""
    candidates_by_url: dict[str, Candidate] = {}
    for section, match_type in (("exact_matches", "exact"), ("visual_matches", "visual")):
        matches = payload.get(section, [])
        if not isinstance(matches, list):
            continue
        for item in matches:
            if not isinstance(item, dict):
                continue
            url = item.get("link")
            if not isinstance(url, str):
                continue
            parsed = urlparse(url)
            host = parsed.hostname.lower() if parsed.hostname else ""
            platform = _platform_for_host(host)
            if parsed.scheme not in {"http", "https"} or platform is None:
                continue
            candidate = Candidate(
                url=url,
                title=str(item.get("title", "")),
                platform=platform,
                match_type=match_type,
                position=item.get("position") if isinstance(item.get("position"), int) else None,
                source=str(item.get("source", "")),
                thumbnail_url=_thumbnail_url(item),
            )
            existing = candidates_by_url.get(url)
            if existing is None or (existing.match_type != "exact" and match_type == "exact"):
                candidates_by_url[url] = candidate
    return list(candidates_by_url.values())
