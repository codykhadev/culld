from pathlib import Path

import cv2

from app.analysis.hashing import compute_phash, hamming_distance

FIXTURES = Path(__file__).parent / "fixtures" / "burst_duplicates"


def _phash(filename: str) -> str:
    image = cv2.imread(str(FIXTURES / filename))
    return compute_phash(image)


def test_burst_frames_are_close_in_hash_distance():
    burst_hashes = [_phash(f"burst_{i}.jpg") for i in range(4)]
    for i in range(len(burst_hashes)):
        for j in range(i + 1, len(burst_hashes)):
            assert hamming_distance(burst_hashes[i], burst_hashes[j]) <= 8


def test_different_scene_is_far_from_burst_frames():
    burst_hash = _phash("burst_0.jpg")
    different_hash = _phash("different_scene.jpg")
    assert hamming_distance(burst_hash, different_hash) > 8


def test_identical_image_has_zero_distance():
    h = _phash("burst_0.jpg")
    assert hamming_distance(h, h) == 0
