import math

import mediapipe as mp
import numpy as np

from app.analysis.face_detection import BoundingBox
from app.config import EAR_THRESHOLD

_mp_face_mesh = mp.solutions.face_mesh

# Indices into MediaPipe's 468-point face mesh: [outer_corner, top_1,
# top_2, inner_corner, bottom_1, bottom_2] tracing each eye's outline.
_RIGHT_EYE = [33, 160, 158, 133, 153, 144]
_LEFT_EYE = [362, 385, 387, 263, 373, 380]


def _dist(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _eye_aspect_ratio(points: list[tuple[float, float]]) -> float:
    """Vertical eyelid gap over horizontal eye width — drops toward zero
    as the eye closes, since the gap collapses but the width doesn't."""
    p1, p2, p3, p4, p5, p6 = points
    vertical = _dist(p2, p6) + _dist(p3, p5)
    horizontal = 2 * _dist(p1, p4)
    return vertical / horizontal


def _detect_single_face_eyes_state(image: np.ndarray) -> str:
    """Runs FaceMesh directly on `image` (assumed to already be roughly
    face-sized, e.g. a crop) and classifies its eyes open/closed."""
    height, width = image.shape[:2]
    rgb_image = image[:, :, ::-1]  # OpenCV loads BGR; MediaPipe expects RGB

    with _mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=False,
        min_detection_confidence=0.3,
    ) as face_mesh:
        result = face_mesh.process(rgb_image)

    if not result.multi_face_landmarks:
        return "no_face_detected"

    landmarks = result.multi_face_landmarks[0].landmark

    def pixel_points(indices: list[int]) -> list[tuple[float, float]]:
        return [(landmarks[i].x * width, landmarks[i].y * height) for i in indices]

    right_ear = _eye_aspect_ratio(pixel_points(_RIGHT_EYE))
    left_ear = _eye_aspect_ratio(pixel_points(_LEFT_EYE))
    avg_ear = (right_ear + left_ear) / 2
    return "closed" if avg_ear < EAR_THRESHOLD else "open"


def detect_eyes_state(image: np.ndarray, face_boxes: list[BoundingBox] | None = None) -> str:
    """Returns "open", "closed", or "no_face_detected". With multiple
    face_boxes, "closed" wins if any single face has closed eyes — a
    group photo where one person blinked is usually the shot to reject.
    """
    if not face_boxes:
        return _detect_single_face_eyes_state(image)

    any_closed = False
    any_open = False

    for x1, y1, x2, y2 in face_boxes:
        crop = image[y1:y2, x1:x2]
        if crop.size == 0:
            continue
        state = _detect_single_face_eyes_state(crop)
        if state == "closed":
            any_closed = True
        elif state == "open":
            any_open = True

    if any_closed:
        return "closed"
    if any_open:
        return "open"
    return "no_face_detected"
