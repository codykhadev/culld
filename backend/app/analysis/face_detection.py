import cv2
import mediapipe as mp
import numpy as np

_mp_face_detection = mp.solutions.face_detection

BoundingBox = tuple[int, int, int, int]  # (x1, y1, x2, y2) in pixel coordinates

# MediaPipe's face detector works on the whole frame in one pass, and on
# very high-resolution camera photos (20+ MP) it silently fails to find
# faces that are perfectly visible at a normal viewing size. Downscaling
# to a modest working resolution before detection fixes this reliably.
_DETECTION_MAX_DIMENSION = 1000


def detect_primary_face_box(image: np.ndarray, min_confidence: float = 0.4) -> BoundingBox | None:
    """Returns the pixel bounding box (in the original image's coordinate
    space) of the largest detected face, or None if no face is found."""
    height, width = image.shape[:2]

    scale = min(1.0, _DETECTION_MAX_DIMENSION / max(height, width))
    detection_image = cv2.resize(image, (int(width * scale), int(height * scale))) if scale < 1.0 else image
    detection_height, detection_width = detection_image.shape[:2]
    rgb_image = detection_image[:, :, ::-1]

    with _mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=min_confidence) as detector:
        result = detector.process(rgb_image)

    if not result.detections:
        return None

    boxes: list[BoundingBox] = []
    for detection in result.detections:
        rel_box = detection.location_data.relative_bounding_box
        x1 = max(0, int(rel_box.xmin * detection_width / scale))
        y1 = max(0, int(rel_box.ymin * detection_height / scale))
        x2 = min(width, x1 + int(rel_box.width * detection_width / scale))
        y2 = min(height, y1 + int(rel_box.height * detection_height / scale))
        if x2 > x1 and y2 > y1:
            boxes.append((x1, y1, x2, y2))

    if not boxes:
        return None

    return max(boxes, key=lambda box: (box[2] - box[0]) * (box[3] - box[1]))


def pad_box(box: BoundingBox, image_shape: tuple[int, ...], padding_ratio: float = 0.3) -> BoundingBox:
    """Grow a box outward so landmark/sharpness analysis isn't cut off
    right at the detector's (often slightly tight) face edge."""
    x1, y1, x2, y2 = box
    height, width = image_shape[:2]
    pad_x = int((x2 - x1) * padding_ratio)
    pad_y = int((y2 - y1) * padding_ratio)
    return (
        max(0, x1 - pad_x),
        max(0, y1 - pad_y),
        min(width, x2 + pad_x),
        min(height, y2 + pad_y),
    )
