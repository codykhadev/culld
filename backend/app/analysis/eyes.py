import math

import mediapipe as mp
import numpy as np

from app.analysis.face_detection import BoundingBox
from app.config import EAR_THRESHOLD

_mp_face_mesh = mp.solutions.face_mesh

# Landmark indices into MediaPipe's 468-point face mesh that trace each
# eye's outline: [outer_corner, top_1, top_2, inner_corner, bottom_1, bottom_2]
_RIGHT_EYE = [33, 160, 158, 133, 153, 144]
_LEFT_EYE = [362, 385, 387, 263, 373, 380]


def _dist(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _eye_aspect_ratio(points: list[tuple[float, float]]) -> float:
    """EAR = (vertical eyelid gaps) / (horizontal eye width).

    Open eyes have a large vertical gap relative to width -> high EAR.
    Closed eyes collapse vertically -> EAR drops toward zero.
    """
    p1, p2, p3, p4, p5, p6 = points
    vertical = _dist(p2, p6) + _dist(p3, p5)
    horizontal = 2 * _dist(p1, p4)
    return vertical / horizontal


def detect_eyes_state(image: np.ndarray, face_box: BoundingBox | None = None) -> str:
    """Returns "open", "closed", or "no_face_detected".

    If face_box (from face_detection.detect_primary_face_box, already
    padded) is given, landmarks are computed on that cropped region —
    FaceMesh's own built-in detector struggles on high-resolution photos
    where the face is a small fraction of the frame, so cropping to a
    known face location first makes detection far more reliable. Falls
    back to the whole frame if the crop somehow doesn't yield landmarks.
    """
    candidates = []
    if face_box is not None:
        x1, y1, x2, y2 = face_box
        crop = image[y1:y2, x1:x2]
        if crop.size > 0:
            candidates.append(crop)
    candidates.append(image)

    with _mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=False,
        min_detection_confidence=0.3,
    ) as face_mesh:
        for candidate in candidates:
            height, width = candidate.shape[:2]
            rgb_image = candidate[:, :, ::-1]  # OpenCV loads BGR; MediaPipe expects RGB
            result = face_mesh.process(rgb_image)
            if not result.multi_face_landmarks:
                continue

            landmarks = result.multi_face_landmarks[0].landmark

            def pixel_points(indices: list[int]) -> list[tuple[float, float]]:
                return [(landmarks[i].x * width, landmarks[i].y * height) for i in indices]

            right_ear = _eye_aspect_ratio(pixel_points(_RIGHT_EYE))
            left_ear = _eye_aspect_ratio(pixel_points(_LEFT_EYE))
            avg_ear = (right_ear + left_ear) / 2
            return "closed" if avg_ear < EAR_THRESHOLD else "open"

    return "no_face_detected"
