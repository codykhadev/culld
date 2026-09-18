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


def _detect_faces_in_region(region: np.ndarray, x_offset: int, y_offset: int, min_confidence: float) -> list[BoundingBox]:
    """Run the detector on `region` and map results back into the
    original full image's coordinate space via x_offset/y_offset."""
    region_height, region_width = region.shape[:2]
    scale = min(1.0, _DETECTION_MAX_DIMENSION / max(region_height, region_width))
    detection_image = (
        cv2.resize(region, (int(region_width * scale), int(region_height * scale)))
        if scale < 1.0
        else region
    )
    detection_height, detection_width = detection_image.shape[:2]
    rgb_image = detection_image[:, :, ::-1]

    with _mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=min_confidence) as detector:
        result = detector.process(rgb_image)

    if not result.detections:
        return []

    boxes: list[BoundingBox] = []
    for detection in result.detections:
        rel_box = detection.location_data.relative_bounding_box
        x1 = x_offset + max(0, int(rel_box.xmin * detection_width / scale))
        y1 = y_offset + max(0, int(rel_box.ymin * detection_height / scale))
        x2 = x_offset + int((rel_box.xmin + rel_box.width) * detection_width / scale)
        y2 = y_offset + int((rel_box.ymin + rel_box.height) * detection_height / scale)
        if x2 > x1 and y2 > y1:
            boxes.append((x1, y1, x2, y2))
    return boxes


def _iou(box_a: BoundingBox, box_b: BoundingBox) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0
    intersection = (ix2 - ix1) * (iy2 - iy1)
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    return intersection / (area_a + area_b - intersection)


def _deduplicate_boxes(boxes: list[BoundingBox], iou_threshold: float = 0.3) -> list[BoundingBox]:
    """Adjacent/overlapping tiles can each detect the same face straddling
    their border; keep the larger box and drop near-duplicates."""
    boxes_by_area_desc = sorted(boxes, key=lambda box: (box[2] - box[0]) * (box[3] - box[1]), reverse=True)
    kept: list[BoundingBox] = []
    for box in boxes_by_area_desc:
        if all(_iou(box, existing) < iou_threshold for existing in kept):
            kept.append(box)
    return kept


def detect_all_face_boxes(image: np.ndarray, min_confidence: float = 0.4) -> list[BoundingBox]:
    """Detect every face in the image, including small/distant faces in a
    busy group photo.

    Tries the whole frame first (fast, and sufficient for portraits/small
    groups). If that finds nothing, falls back to a slower pass over a
    2x2 grid of overlapping tiles — a face too small to register against
    the full frame becomes proportionally larger within a tile, which is
    what the detector actually needs to find it.
    """
    height, width = image.shape[:2]

    whole_frame_boxes = _detect_faces_in_region(image, 0, 0, min_confidence)
    if whole_frame_boxes:
        return whole_frame_boxes

    tile_boxes: list[BoundingBox] = []
    tile_height, tile_width = height // 2, width // 2
    pad_h, pad_w = int(tile_height * 0.15), int(tile_width * 0.15)
    for row in range(2):
        for col in range(2):
            y1 = max(0, row * tile_height - pad_h)
            y2 = min(height, (row + 1) * tile_height + pad_h)
            x1 = max(0, col * tile_width - pad_w)
            x2 = min(width, (col + 1) * tile_width + pad_w)
            tile = image[y1:y2, x1:x2]
            tile_boxes.extend(_detect_faces_in_region(tile, x1, y1, min_confidence))

    return _deduplicate_boxes(tile_boxes)


def detect_primary_face_box(image: np.ndarray, min_confidence: float = 0.4) -> BoundingBox | None:
    """Convenience wrapper for the single dominant face in the frame (e.g.
    a portrait) — the largest of all detected faces, or None."""
    boxes = detect_all_face_boxes(image, min_confidence)
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
