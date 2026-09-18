from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from app.config import THUMBNAIL_SIZE, UPLOAD_DIR


def decode_image(raw_bytes: bytes) -> np.ndarray:
    buffer = np.frombuffer(raw_bytes, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image — unsupported or corrupt file")
    return image


def session_dirs(session_id: str) -> tuple[Path, Path]:
    original_dir = UPLOAD_DIR / session_id / "original"
    thumb_dir = UPLOAD_DIR / session_id / "thumbs"
    original_dir.mkdir(parents=True, exist_ok=True)
    thumb_dir.mkdir(parents=True, exist_ok=True)
    return original_dir, thumb_dir


def save_upload(session_id: str, photo_id: str, filename: str, raw_bytes: bytes) -> tuple[Path, Path]:
    original_dir, thumb_dir = session_dirs(session_id)
    suffix = Path(filename).suffix or ".jpg"

    original_path = original_dir / f"{photo_id}{suffix}"
    original_path.write_bytes(raw_bytes)

    thumb_path = thumb_dir / f"{photo_id}.jpg"
    with Image.open(original_path) as img:
        img = img.convert("RGB")
        img.thumbnail(THUMBNAIL_SIZE)
        img.save(thumb_path, "JPEG", quality=85)

    return original_path, thumb_path
