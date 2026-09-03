from .detector import DetectedFace

class FaceEncoder:
    def encode(self, faces: list[DetectedFace]) -> list[list[float]]:
        embeddings = []
        for face in faces:
            if face.raw is None or getattr(face.raw, "embedding", None) is None:
                raise RuntimeError("Face detector did not provide an embedding")
            embeddings.append([float(value) for value in face.raw.embedding])
        return embeddings
