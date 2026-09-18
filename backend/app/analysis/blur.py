import cv2
import numpy as np

from app.analysis.face_detection import BoundingBox

# Raw Laplacian variance drops sharply as resolution increases even for a
# genuinely sharp photo, so scores aren't comparable across camera files of
# different sizes unless we normalize to a fixed width first.
_ANALYSIS_WIDTH = 800


def _resize_for_analysis(gray: np.ndarray) -> np.ndarray:
    height, width = gray.shape
    if width <= _ANALYSIS_WIDTH:
        return gray
    scale = _ANALYSIS_WIDTH / width
    return cv2.resize(gray, (_ANALYSIS_WIDTH, int(height * scale)))


def _laplacian_variance(gray_region: np.ndarray) -> float:
    return float(cv2.Laplacian(gray_region, cv2.CV_64F).var())


def compute_blur_score(image: np.ndarray, subject_box: BoundingBox | None = None) -> float:
    """Higher = sharper (Laplacian variance). Scores only within
    subject_box when given — otherwise a photographer's intentional
    shallow-depth-of-field background blur drags the whole-frame score
    down and wrongly flags an in-focus subject as blurry.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if subject_box is not None:
        x1, y1, x2, y2 = subject_box
        region = gray[y1:y2, x1:x2]
        if region.size > 0:
            gray = region
    return _laplacian_variance(_resize_for_analysis(gray))


def is_blurry(blur_score: float, threshold: float) -> bool:
    return blur_score < threshold
