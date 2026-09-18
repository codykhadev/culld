from fastapi import APIRouter, HTTPException, UploadFile

from app.analysis.blur import compute_blur_score, is_blurry
from app.models import BlurResult
from app.storage import decode_image

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("/blur", response_model=BlurResult)
async def analyze_blur(file: UploadFile) -> BlurResult:
    raw_bytes = await file.read()
    try:
        image = decode_image(raw_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    score = compute_blur_score(image)
    return BlurResult(blur_score=score, is_blurry=is_blurry(score))
