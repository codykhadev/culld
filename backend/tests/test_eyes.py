from pathlib import Path

import cv2
import pytest

from app.analysis.eyes import detect_eyes_state
from app.analysis.face_detection import detect_all_face_boxes, pad_box

FIXTURES = Path(__file__).parent / "fixtures"


def _load(*parts: str):
    """Real personal photos aren't committed to the repo (see .gitignore),
    so skip these tests instead of failing when they're not present locally.
    """
    path = FIXTURES.joinpath(*parts)
    if not path.exists():
        pytest.skip(f"local-only fixture not present: {path}")
    return cv2.imread(str(path))


def test_open_eyes_photo_classified_as_open():
    image = _load("eyes_open", "two_people.jpg")
    assert detect_eyes_state(image) == "open"


def test_closed_eyes_photo_classified_as_closed():
    image = _load("eyes_closed", "squint.jpg")
    assert detect_eyes_state(image) == "closed"


@pytest.mark.parametrize("filename", ["campus_view.jpg", "paragliders.jpg"])
def test_no_face_photos_degrade_gracefully(filename):
    image = _load("no_face", filename)
    assert detect_eyes_state(image) == "no_face_detected"


def test_group_photo_with_multiple_faces_is_not_flagged_no_face():
    """Regression test: a busy group photo used to come back as
    "no_face_detected" even though it clearly has faces in it."""
    image = _load("group_photos", "small_group.jpg")
    boxes = detect_all_face_boxes(image)
    padded_boxes = [pad_box(box, image.shape) for box in boxes]
    assert detect_eyes_state(image, face_boxes=padded_boxes) in ("open", "closed")
