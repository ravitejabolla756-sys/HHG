from dataclasses import dataclass
from pathlib import Path
import time

import requests


SERPAPI_IMAGE_ENDPOINT = "https://serpapi.com/image"
SERPAPI_SEARCH_ENDPOINT = "https://serpapi.com/search.json"
SERPAPI_MAX_UPLOAD_BYTES = 500 * 1024


@dataclass(frozen=True)
class SearchResponse:
    provider: str
    status: str
    data: dict
    visual_match_count: int
    exact_match_count: int

    @property
    def result_count(self) -> int:
        return self.visual_match_count + self.exact_match_count


class ReverseSearchClient:
    def __init__(self, api_key: str, timeout: int = 60, retries: int = 2):
        self.api_key = api_key
        self.timeout = timeout
        self.retries = retries

    def search(self, image_path: str | Path) -> SearchResponse:
        path = Path(image_path)
        if not self.api_key:
            raise RuntimeError("SERPAPI_API_KEY is not configured")
        if not path.is_file():
            raise RuntimeError(f"Input image does not exist: {path}")
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            raise RuntimeError("SerpApi Image API accepts only JPG, JPEG, PNG, or WebP")
        if path.stat().st_size > SERPAPI_MAX_UPLOAD_BYTES:
            raise RuntimeError("SerpApi Image API input exceeds the 500 KB upload limit")

        upload = self._upload_image(path)
        image_id = upload.get("image_id")
        if not isinstance(image_id, str) or not image_id:
            raise RuntimeError("SerpApi Image API succeeded without returning image_id")

        payload = self._request_json(
            "GET",
            SERPAPI_SEARCH_ENDPOINT,
            params={
                "api_key": self.api_key,
                "engine": "google_lens",
                "image_id": image_id,
                "type": "all",
                "no_cache": "true",
                "output": "json",
            },
            operation="Google Lens search",
        )
        visual_matches = payload.get("visual_matches", [])
        exact_matches = payload.get("exact_matches", [])
        return SearchResponse(
            provider="SerpApi Google Lens",
            status="ok",
            data=payload,
            visual_match_count=len(visual_matches) if isinstance(visual_matches, list) else 0,
            exact_match_count=len(exact_matches) if isinstance(exact_matches, list) else 0,
        )

    def _upload_image(self, path: Path) -> dict:
        with path.open("rb") as image:
            return self._request_json(
                "POST",
                SERPAPI_IMAGE_ENDPOINT,
                data={"api_key": self.api_key},
                files={"image": (path.name, image, self._content_type(path))},
                operation="image upload",
            )

    def _request_json(self, method: str, url: str, operation: str, **kwargs) -> dict:
        last_error = "unknown error"
        for attempt in range(self.retries + 1):
            try:
                response = requests.request(method, url, timeout=self.timeout, **kwargs)
                if response.status_code >= 400:
                    last_error = f"HTTP {response.status_code}"
                else:
                    payload = response.json()
                    if not isinstance(payload, dict):
                        last_error = "non-object JSON response"
                    elif payload.get("error"):
                        last_error = str(payload["error"]).replace(self.api_key, "[REDACTED]")
                    else:
                        return payload
            except requests.Timeout:
                last_error = "request timed out"
            except requests.RequestException as exc:
                last_error = str(exc).replace(self.api_key, "[REDACTED]")
            except ValueError:
                last_error = "invalid JSON response"
            if attempt < self.retries:
                time.sleep(2**attempt)
        raise RuntimeError(f"SerpApi {operation} failed after retries: {last_error}")

    @staticmethod
    def _content_type(path: Path) -> str:
        return {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }[path.suffix.lower()]
