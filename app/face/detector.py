from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any

@dataclass(frozen=True)
class DetectedFace:
    bbox: tuple[float, float, float, float]
    raw: Any = None

class FaceDetector:
    def __init__(self, model_name: str = "buffalo_l", model_root: str | Path | None = None):
        try:
            from insightface.app import FaceAnalysis
        except ImportError as exc:
            raise RuntimeError("InsightFace is required for face detection") from exc
        default_root = Path(__file__).resolve().parents[2] / ".models" / "insightface"
        root = Path(model_root or os.getenv("INSIGHTFACE_HOME", default_root))
        root.mkdir(parents=True, exist_ok=True)
        self._analysis = FaceAnalysis(name=model_name, root=str(root), providers=["CPUExecutionProvider"])
        self._analysis.prepare(ctx_id=0, det_size=(640, 640))

    def detect(self, image_path: str | Path) -> list[DetectedFace]:
        import cv2
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Unable to read image: {image_path}")
        return [DetectedFace(tuple(map(float, face.bbox)), face) for face in self._analysis.get(image)]
