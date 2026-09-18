import numpy as np

from app.analysis.blur import compute_blur_score, is_blurry
from app.analysis.eyes import detect_eyes_state
from app.analysis.face_detection import detect_all_face_boxes, pad_box
from app.analysis.hashing import compute_phash
from app.config import BLUR_THRESHOLD, FACE_BLUR_THRESHOLD


def analyze_photo(image: np.ndarray) -> dict:
    """Run all per-image analyzers on a single decoded image.

    Face detection runs once and its result is shared by both blur
    scoring and eyes-state detection. Blur scoring only zooms into a
    subject region when there's exactly one clear subject (a portrait) —
    the face-crop threshold was calibrated for that single-subject case,
    and group photos aren't usually shot with shallow depth of field
    anyway, so those fall back to whole-frame scoring.
    """
    face_boxes = detect_all_face_boxes(image)
    padded_boxes = [pad_box(box, image.shape) for box in face_boxes]

    if len(padded_boxes) == 1:
        blur_score = compute_blur_score(image, subject_box=padded_boxes[0])
        threshold = FACE_BLUR_THRESHOLD
    else:
        blur_score = compute_blur_score(image)
        threshold = BLUR_THRESHOLD

    return {
        "blur_score": blur_score,
        "is_blurry": is_blurry(blur_score, threshold),
        "eyes_state": detect_eyes_state(image, face_boxes=padded_boxes),
        "phash": compute_phash(image),
    }
