"""One-off script to generate a synthetic photo "burst": several
near-identical frames (simulating a photographer firing off a few shots
in a row — tiny handshake shifts, slight brightness/exposure drift) plus
one clearly different scene as a control. No real people involved, so
these are safe to commit unlike the eyes-open/closed fixtures.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

OUT_DIR = "burst_duplicates"


def make_base_scene(size=400):
    """A scene with enough structure that perceptual hashing has real
    content to work with (a plain gradient would hash too trivially)."""
    img = Image.new("RGB", (size, size), (200, 210, 225))
    draw = ImageDraw.Draw(img)
    draw.ellipse([80, 60, 320, 300], fill=(220, 140, 90))  # "subject"
    draw.rectangle([0, 300, size, size], fill=(90, 140, 80))  # "ground"
    draw.polygon([(40, 300), (120, 150), (200, 300)], fill=(70, 90, 60))  # "tree"
    for i in range(15):
        draw.line([(i * 27, 0), (i * 27, 60)], fill=(150, 170, 200), width=2)
    return img


def jittered_burst_frame(base: Image.Image, dx: int, dy: int, brightness: float) -> Image.Image:
    """Simulate a slightly shaky, slightly differently-exposed shot from
    the same burst: shift a few pixels and nudge the brightness."""
    shifted = Image.new("RGB", base.size, (200, 210, 225))
    shifted.paste(base, (dx, dy))
    return ImageEnhance.Brightness(shifted).enhance(brightness)


def make_different_scene(size=400):
    """A distinctly different scene — should NOT group with the burst."""
    img = Image.new("RGB", (size, size), (30, 30, 40))
    draw = ImageDraw.Draw(img)
    rng = np.random.default_rng(42)
    for _ in range(40):
        x, y = rng.integers(0, size, 2)
        r = rng.integers(5, 20)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=tuple(rng.integers(180, 255, 3).tolist()))
    return img


def main():
    base = make_base_scene()

    # 4 near-identical "burst" frames: small shifts + brightness drift
    variants = [
        (0, 0, 1.0),
        (2, -1, 1.05),
        (-1, 2, 0.95),
        (1, 1, 1.02),
    ]
    for i, (dx, dy, brightness) in enumerate(variants):
        frame = jittered_burst_frame(base, dx, dy, brightness)
        frame.save(f"{OUT_DIR}/burst_{i}.jpg", quality=92)

    # 1 clearly different photo — should end up in its own group
    make_different_scene().save(f"{OUT_DIR}/different_scene.jpg", quality=92)

    print("Generated 4 burst frames + 1 distinct control image.")


if __name__ == "__main__":
    main()
