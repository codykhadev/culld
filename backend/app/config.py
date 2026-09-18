from pathlib import Path

# Whole-frame threshold (landscapes, group shots) — tuned against the
# synthetic fixtures in tests/fixtures/.
BLUR_THRESHOLD = 100.0

# Separate, much lower threshold for a cropped face region: real photo
# texture has far less raw edge contrast than the synthetic fixtures, so
# it sits on its own scale. Calibrated against real face crops — sharp
# ones scored 22.7-462.7, mildly blurred versions dropped to 2-5.3.
FACE_BLUR_THRESHOLD = 12.0

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
THUMBNAIL_SIZE = (320, 320)

# Below this Eye Aspect Ratio, eyes are classified "closed". Calibrated
# against real photos (~0.149 open, ~0.119 closed) — lower than the ~0.2-0.3
# you'll see in dlib tutorials, since MediaPipe's landmarks give a
# different absolute EAR scale.
EAR_THRESHOLD = 0.13

# Max bit difference between two perceptual hashes (out of 64) to count
# as the same burst.
HASH_DISTANCE_THRESHOLD = 8
