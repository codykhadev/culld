import imagehash
import numpy as np
from PIL import Image


def compute_phash(image: np.ndarray) -> str:
    """Unlike a cryptographic hash, visually similar images get similar
    hashes — near-identical burst shots land only a few bits apart."""
    rgb_image = image[:, :, ::-1]  # OpenCV loads BGR; PIL expects RGB
    pil_image = Image.fromarray(rgb_image)
    return str(imagehash.phash(pil_image))


def hamming_distance(hash_a: str, hash_b: str) -> int:
    """Number of differing bits between two perceptual hashes — a cheap
    similarity proxy that avoids ever comparing raw pixels directly."""
    return imagehash.hex_to_hash(hash_a) - imagehash.hex_to_hash(hash_b)
