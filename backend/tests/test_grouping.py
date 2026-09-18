from pathlib import Path

import cv2

from app.analysis.grouping import PhotoForGrouping, group_photos
from app.analysis.hashing import compute_phash

FIXTURES = Path(__file__).parent / "fixtures" / "burst_duplicates"


def _photo(photo_id: str, filename: str, blur_score: float, eyes_state: str | None = None):
    image = cv2.imread(str(FIXTURES / filename))
    return PhotoForGrouping(
        id=photo_id,
        phash=compute_phash(image),
        blur_score=blur_score,
        eyes_state=eyes_state,
    )


def test_burst_frames_land_in_one_group_and_different_scene_does_not():
    photos = [
        _photo("burst-0", "burst_0.jpg", blur_score=100),
        _photo("burst-1", "burst_1.jpg", blur_score=150),
        _photo("burst-2", "burst_2.jpg", blur_score=90),
        _photo("burst-3", "burst_3.jpg", blur_score=120),
        _photo("control", "different_scene.jpg", blur_score=200),
    ]

    results = group_photos(photos)

    burst_group_ids = {results[f"burst-{i}"].group_id for i in range(4)}
    assert len(burst_group_ids) == 1
    assert burst_group_ids != {None}

    assert results["control"].group_id is None
    assert results["control"].is_recommended_keeper is None


def test_keeper_is_sharpest_photo_in_group_when_no_eyes_data():
    photos = [
        _photo("a", "burst_0.jpg", blur_score=50),
        _photo("b", "burst_1.jpg", blur_score=300),  # sharpest
        _photo("c", "burst_2.jpg", blur_score=100),
    ]

    results = group_photos(photos)

    assert results["b"].is_recommended_keeper is True
    assert results["a"].is_recommended_keeper is False
    assert results["c"].is_recommended_keeper is False


def test_keeper_prefers_eyes_open_over_just_sharpness():
    photos = [
        _photo("blurry_open", "burst_0.jpg", blur_score=50, eyes_state="open"),
        _photo("sharp_closed", "burst_1.jpg", blur_score=300, eyes_state="closed"),
    ]

    results = group_photos(photos)

    assert results["blurry_open"].is_recommended_keeper is True
    assert results["sharp_closed"].is_recommended_keeper is False
