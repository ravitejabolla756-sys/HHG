from app.face.detector import DetectedFace
def test_face_detection_interface():
    face = DetectedFace((1.0, 2.0, 3.0, 4.0))
    assert face.bbox == (1.0, 2.0, 3.0, 4.0)
