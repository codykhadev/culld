from pathlib import Path

import cv2
import pytest

from app.analysis.blur import compute_blur_score, is_blurry
from app.config import BLUR_THRESHOLD

FIXTURES = Path(__file__).parent / "fixtures"
SCENES = ["checkerboard", "noise", "text_scene"]


@pytest.mark.parametrize("scene", SCENES)
def test_sharp_scores_higher_than_blurry_version(scene):
    sharp = cv2.imread(str(FIXTURES / "sharp" / f"{scene}.jpg"))
    blurry = cv2.imread(str(FIXTURES / "blurry" / f"{scene}.jpg"))

    sharp_score = compute_blur_score(sharp)
    blurry_score = compute_blur_score(blurry)

    assert sharp_score > blurry_score


@pytest.mark.parametrize("scene", SCENES)
def test_sharp_images_are_not_flagged_blurry(scene):
    sharp = cv2.imread(str(FIXTURES / "sharp" / f"{scene}.jpg"))
    assert is_blurry(compute_blur_score(sharp), BLUR_THRESHOLD) is False


@pytest.mark.parametrize("scene", SCENES)
def test_blurry_images_are_flagged_blurry(scene):
    blurry = cv2.imread(str(FIXTURES / "blurry" / f"{scene}.jpg"))
    assert is_blurry(compute_blur_score(blurry), BLUR_THRESHOLD) is True


def test_blur_score_is_consistent_across_high_resolutions():
    """Regression test: raw Laplacian variance drops sharply as resolution
    increases even for a genuinely sharp image, which used to cause real
    high-resolution camera photos to be wrongly flagged as blurry. Any
    input wider than the analysis width gets resized down to the same
    working resolution, so two differently-sized versions of the same
    sharp content (both above that width) should score similarly.
    """
    sharp = cv2.imread(str(FIXTURES / "sharp" / "text_scene.jpg"))
    height, width = sharp.shape[:2]

    moderately_large = cv2.resize(sharp, (1000, int(height * 1000 / width)))
    very_large = cv2.resize(sharp, (3000, int(height * 3000 / width)))

    score_moderate = compute_blur_score(moderately_large)
    score_large = compute_blur_score(very_large)

    assert score_moderate == pytest.approx(score_large, rel=0.3)
