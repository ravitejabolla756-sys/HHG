from dataclasses import dataclass
from ipaddress import ip_address
import socket
from urllib.parse import urlparse

import cv2
import numpy as np
import requests

from ..face.detector import FaceDetector
from ..face.encoder import FaceEncoder
from .parser import Candidate


DEFAULT_FACE_SIMILARITY_THRESHOLD = 0.45
MAX_THUMBNAIL_BYTES = 5 * 1024 * 1024
TRUSTED_THUMBNAIL_DOMAINS = ("gstatic.com", "googleusercontent.com", "serpapi.com")


@dataclass(frozen=True)
class CandidateVerification:
    candidate: Candidate
    verified: bool
    method: str
    evidence: str
    similarity: float | None = None
    detected_faces: int = 0


@dataclass(frozen=True)
class MatchSelection:
    match: Candidate
    evidence: CandidateVerification
    evaluations: list[CandidateVerification]


class CandidateVerificationError(RuntimeError):
    def __init__(self, evaluations: list[CandidateVerification]):
        self.evaluations = evaluations
        super().__init__(
            "No social-media candidate could be verified against the input face; refusing blockchain registration"
        )


class CandidateVerifier:
    def __init__(
        self,
        detector: FaceDetector,
        encoder: FaceEncoder,
        threshold: float = DEFAULT_FACE_SIMILARITY_THRESHOLD,
        timeout: int = 15,
    ):
        if not 0 < threshold <= 1:
            raise ValueError("Face similarity threshold must be in (0, 1]")
        self.detector = detector
        self.encoder = encoder
        self.threshold = threshold
        self.timeout = timeout

    def select_match(self, candidates: list[Candidate], reference_embedding: list[float]) -> MatchSelection:
        if not candidates:
            raise CandidateVerificationError([])
        evaluations = [self.verify(candidate, reference_embedding) for candidate in candidates]
        verified = [evaluation for evaluation in evaluations if evaluation.verified]
        if not verified:
            raise CandidateVerificationError(evaluations)
        best = max(
            verified,
            key=lambda item: (
                item.similarity or 0.0,
                item.candidate.match_type == "exact",
                -(item.candidate.position or 1_000_000),
            ),
        )
        return MatchSelection(best.candidate, best, evaluations)

    def verify(self, candidate: Candidate, reference_embedding: list[float]) -> CandidateVerification:
        method = "InsightFace cosine similarity against provider-returned Lens thumbnail"
        if not candidate.thumbnail_url:
            return CandidateVerification(candidate, False, method, "rejected: Lens result supplied no thumbnail")
        try:
            image = self._download_thumbnail(candidate.thumbnail_url)
            faces = self.detector.detect_array(image)
            if not faces:
                return CandidateVerification(candidate, False, method, "rejected: no face detected in Lens thumbnail")
            similarities = [self._cosine_similarity(reference_embedding, value) for value in self.encoder.encode(faces)]
            similarity = max(similarities)
            verified = similarity >= self.threshold
            evidence = (
                f"verified: best face similarity {similarity:.4f} >= {self.threshold:.2f}"
                if verified
                else f"rejected: best face similarity {similarity:.4f} < {self.threshold:.2f}"
            )
            return CandidateVerification(candidate, verified, method, evidence, similarity, len(faces))
        except Exception as exc:
            return CandidateVerification(candidate, False, method, f"rejected: thumbnail verification failed ({exc})")

    def _download_thumbnail(self, url: str) -> np.ndarray:
        self._validate_thumbnail_url(url)
        with requests.get(url, timeout=self.timeout, stream=True) as response:
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "").split(";", 1)[0].lower()
            if not content_type.startswith("image/"):
                raise RuntimeError("thumbnail response was not an image")
            chunks = []
            size = 0
            for chunk in response.iter_content(64 * 1024):
                size += len(chunk)
                if size > MAX_THUMBNAIL_BYTES:
                    raise RuntimeError("thumbnail exceeded 5 MB")
                chunks.append(chunk)
        image = cv2.imdecode(np.frombuffer(b"".join(chunks), dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise RuntimeError("thumbnail could not be decoded")
        return image

    @staticmethod
    def _validate_thumbnail_url(url: str) -> None:
        parsed = urlparse(url)
        host = parsed.hostname.lower() if parsed.hostname else ""
        trusted = any(host == domain or host.endswith("." + domain) for domain in TRUSTED_THUMBNAIL_DOMAINS)
        if parsed.scheme != "https" or not trusted:
            raise RuntimeError("thumbnail host is not a trusted Lens image host")
        for info in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM):
            address = ip_address(info[4][0])
            if not address.is_global:
                raise RuntimeError("thumbnail host resolved to a non-public address")

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        left_vector = np.asarray(left, dtype=np.float32)
        right_vector = np.asarray(right, dtype=np.float32)
        if left_vector.shape != right_vector.shape or left_vector.ndim != 1:
            raise RuntimeError("face embeddings have incompatible dimensions")
        denominator = float(np.linalg.norm(left_vector) * np.linalg.norm(right_vector))
        if denominator == 0:
            raise RuntimeError("face embedding had zero magnitude")
        return float(np.dot(left_vector, right_vector) / denominator)
