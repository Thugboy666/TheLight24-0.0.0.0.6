import os
import pytest

def pytest_addoption(parser):
    parser.addoption("--with-audio", action="store_true", default=False, help="Esegui test audio live")
    parser.addoption("--with-video", action="store_true", default=False, help="Esegui test video live")

@pytest.fixture(scope="session")
def audio_enabled(pytestconfig):
    return pytestconfig.getoption("--with-audio")

@pytest.fixture(scope="session")
def video_enabled(pytestconfig):
    return pytestconfig.getoption("--with-video")

@pytest.fixture(scope="session")
def have_build():
    # verifica che il modulo C++ sia visibile
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "build"))
    try:
        import physics_core  # noqa
        return True
    except Exception:
        return False
