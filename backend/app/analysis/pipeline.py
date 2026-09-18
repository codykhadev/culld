import numpy as np

from app.analysis.blur import compute_blur_score, is_blurry
from app.analysis.eyes import detect_eyes_state
from app.analysis.face_detection import detect_primary_face_box, pad_box
from app.analysis.hashing import compute_phash
from app.config import BLUR_THRESHOLD, FACE_BLUR_THRESHOLD


def analyze_photo(image: np.ndarray) -> dict:
    """Run all per-image analyzers on a single decoded image.

    Face detection runs once and its result is shared by both blur
    scoring (so a photographer's intentional background blur doesn't
    wrongly flag an in-focus subject) and eyes-state detection (so a
    small/distant face in a high-resolution photo is still found).
    """
    face_box = detect_primary_face_box(image)
    padded_box = pad_box(face_box, image.shape) if face_box is not None else None

    blur_score = compute_blur_score(image, subject_box=padded_box)
    threshold = FACE_BLUR_THRESHOLD if padded_box is not None else BLUR_THRESHOLD

    return {
        "blur_score": blur_score,
        "is_blurry": is_blurry(blur_score, threshold),
        "eyes_state": detect_eyes_state(image, face_box=padded_box),
        "phash": compute_phash(image),
    }
