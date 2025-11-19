import pytest

def test_cv_import():
    import cv2
    assert cv2.__version__[:1].isdigit()

@pytest.mark.skip(reason="Test live webcam disabilitato per default")
def test_webcam_open(video_enabled):
    if not video_enabled:
        pytest.skip("Avvia con --with-video per testare la webcam")
    import cv2
    cap = cv2.VideoCapture(0)
    assert cap.isOpened()
    cap.release()
