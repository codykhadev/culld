import shutil
import uuid
from pathlib import Path

import pytest

from app.config import UPLOAD_DIR
from app.storage import decode_image, save_upload


def test_decode_image_rejects_corrupt_bytes():
    with pytest.raises(ValueError):
        decode_image(b"this is not a real image")


def test_save_upload_raises_value_error_on_corrupt_file():
    """Regression test: a corrupt file used to crash the whole upload
    request with an unhandled PIL error instead of being caught and
    marked as a failed photo like decode_image's errors are."""
    session_id = f"test-{uuid.uuid4()}"
    try:
        with pytest.raises(ValueError):
            save_upload(session_id, "photo-1", "fake.jpg", b"this is not a real image")
    finally:
        shutil.rmtree(UPLOAD_DIR / session_id, ignore_errors=True)


def test_save_upload_succeeds_on_a_real_image():
    session_id = f"test-{uuid.uuid4()}"
    fixture = Path(__file__).parent / "fixtures" / "sharp" / "text_scene.jpg"
    try:
        original_path, thumb_path = save_upload(session_id, "photo-1", "text_scene.jpg", fixture.read_bytes())
        assert original_path.exists()
        assert thumb_path.exists()
    finally:
        shutil.rmtree(UPLOAD_DIR / session_id, ignore_errors=True)
