from pathlib import Path

import cv2
import pytest

from app.analysis.face_detection import detect_all_face_boxes, detect_primary_face_box, pad_box

FIXTURES = Path(__file__).parent / "fixtures"


def _load(*parts: str):
    path = FIXTURES.joinpath(*parts)
    if not path.exists():
        pytest.skip(f"local-only fixture not present: {path}")
    return cv2.imread(str(path))


def test_finds_a_face_in_a_real_portrait():
    image = _load("eyes_open", "two_people.jpg")
    box = detect_primary_face_box(image)
    assert box is not None

    x1, y1, x2, y2 = box
    assert x2 > x1
    assert y2 > y1


def test_returns_none_for_a_landscape_with_no_face():
    image = _load("no_face", "campus_view.jpg")
    assert detect_primary_face_box(image) is None


def test_pad_box_grows_the_box_without_leaving_the_image():
    image = _load("eyes_open", "two_people.jpg")
    box = detect_primary_face_box(image)
    padded = pad_box(box, image.shape)

    x1, y1, x2, y2 = padded
    height, width = image.shape[:2]
    assert x1 <= box[0]
    assert y1 <= box[1]
    assert x2 >= box[2]
    assert y2 >= box[3]
    assert 0 <= x1 and x2 <= width
    assert 0 <= y1 and y2 <= height


def test_finds_multiple_small_faces_in_a_group_photo():
    """Regression test: the whole-frame-only detector used to miss every
    face in a busy group photo where each face is a small fraction of a
    high-resolution frame. The tiled fallback should catch several."""
    image = _load("group_photos", "small_group.jpg")
    boxes = detect_all_face_boxes(image)
    assert len(boxes) >= 2
