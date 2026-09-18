import imagehash
import numpy as np
from PIL import Image


def compute_phash(image: np.ndarray) -> str:
    """Perceptual hash: visually similar images get similar hashes, unlike
    a cryptographic hash where a 1-pixel change scrambles the output.
    imagehash resizes the image down, applies a DCT to capture the image's
    low-frequency structure, and encodes that as a compact bit string —
    so near-identical burst shots end up only a few bits apart.
    """
    rgb_image = image[:, :, ::-1]  # OpenCV loads BGR; PIL expects RGB
    pil_image = Image.fromarray(rgb_image)
    return str(imagehash.phash(pil_image))


def hamming_distance(hash_a: str, hash_b: str) -> int:
    """Number of differing bits between two perceptual hashes — a cheap
    similarity proxy that avoids ever comparing raw pixels directly."""
    return imagehash.hex_to_hash(hash_a) - imagehash.hex_to_hash(hash_b)
