from pathlib import Path

# Below this Laplacian-variance score, a whole-frame image (no detected
# subject — e.g. a landscape) is flagged as blurry. Tuned against the
# synthetic sharp/blurry fixtures in tests/fixtures/.
BLUR_THRESHOLD = 100.0

# Separate, much lower threshold for scoring a cropped face/subject region
# in a real photo. Real photographic texture (skin, hair, natural detail)
# has far less raw edge contrast than the synthetic high-contrast fixtures
# above, so it lands on a different numeric scale — this was calibrated
# against real face crops (genuinely sharp faces scored 22.7-462.7;
# mildly blurred versions of the same faces dropped to 2-5.3).
FACE_BLUR_THRESHOLD = 12.0

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
THUMBNAIL_SIZE = (320, 320)

# Eye Aspect Ratio below this is classified as "closed". Tuned against
# real eyes-open/eyes-closed fixture photos (measured ~0.149 open,
# ~0.119 squinting/closed with this landmark set — note MediaPipe's
# face-mesh landmarks give a different absolute EAR scale than the
# classic dlib 68-point formula, so this threshold is lower than typical
# dlib-based EAR thresholds you'll see in tutorials).
EAR_THRESHOLD = 0.13

# Two photos are considered the same "burst" if their perceptual hashes
# differ by at most this many bits (out of 64, for the default phash size).
HASH_DISTANCE_THRESHOLD = 8
