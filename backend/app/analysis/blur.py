import cv2
import numpy as np

from app.analysis.face_detection import BoundingBox

# Raw Laplacian variance drops sharply as image resolution increases, even
# for a genuinely sharp photo (fine edges get diluted across more pixels).
# Resizing to a fixed working width before scoring keeps the score — and
# a single BLUR_THRESHOLD — meaningful whether the input is a phone photo
# or a 30+ megapixel camera file.
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
    """Higher = sharper. Uses the variance of the Laplacian: sharp regions
    have lots of crisp edges (high-frequency detail), so the Laplacian
    (an edge-detection filter) responds strongly and unevenly, giving high
    variance. Blurry regions have smeared edges, so the Laplacian response
    is flatter and the variance is low.

    When subject_box (e.g. a detected face, from face_detection.py) is
    given, sharpness is measured only within that region — otherwise a
    photographer's intentional shallow-depth-of-field background blur
    would drag down the score and wrongly flag an in-focus subject as
    blurry. Falls back to the whole frame when there's no clear subject
    (e.g. a landscape).
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
