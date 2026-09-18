"""One-off script to generate synthetic sharp/blurry test images.

Real photos aren't checked into the repo (large binaries, not reproducible),
so we synthesize a few deterministic images instead: a sharp version has
lots of fine-grained detail (checkerboards, noise, text), and a blurry
version is the same image run through a Gaussian blur. Run this once;
the outputs are small and safe to commit.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_SHARP = "sharp"
OUT_BLURRY = "blurry"


def make_checkerboard(size=400, cell=10):
    arr = np.zeros((size, size), dtype=np.uint8)
    for y in range(0, size, cell):
        for x in range(0, size, cell):
            if ((x // cell) + (y // cell)) % 2 == 0:
                arr[y : y + cell, x : x + cell] = 255
    return Image.fromarray(arr).convert("RGB")


def make_noise(size=400, seed=0):
    rng = np.random.default_rng(seed)
    arr = rng.integers(0, 256, (size, size, 3), dtype=np.uint8)
    return Image.fromarray(arr)


def make_text_scene(size=400):
    img = Image.new("RGB", (size, size), (220, 220, 220))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    except OSError:
        font = ImageFont.load_default()
    for i in range(10):
        draw.text((10, i * 38), f"line {i} sharp edges 0123456789", fill=(0, 0, 0), font=font)
    draw.rectangle([20, 20, 380, 380], outline=(255, 0, 0), width=3)
    return img


def main():
    generators = {
        "checkerboard": make_checkerboard(),
        "noise": make_noise(),
        "text_scene": make_text_scene(),
    }

    for name, img in generators.items():
        img.save(f"{OUT_SHARP}/{name}.jpg", quality=95)
        blurry = img.filter(ImageFilter.GaussianBlur(radius=8))
        blurry.save(f"{OUT_BLURRY}/{name}.jpg", quality=95)

    print(f"Generated {len(generators)} sharp + {len(generators)} blurry fixtures.")


if __name__ == "__main__":
    main()
