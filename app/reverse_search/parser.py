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

def _walk(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in {"url", "link", "source_url"} and isinstance(item, str): yield item, value.get("title", "")
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value: yield from _walk(item)

def _platform_for_host(host: str) -> str | None:
    for domain, platform in SOCIAL_DOMAINS.items():
        if host == domain or host.endswith("." + domain):
            return platform
    return None

def parse_candidates(payload: dict) -> list[Candidate]:
    seen, result = set(), []
    for url, title in _walk(payload):
        parsed = urlparse(url)
        host = parsed.netloc.lower().split(":")[0]
        platform = _platform_for_host(host)
        if parsed.scheme not in {"http", "https"} or platform is None or url in seen: continue
        seen.add(url)
        result.append(Candidate(url, str(title), platform))
    return result
