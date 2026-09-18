from pathlib import Path

from pydantic import BaseModel


class BlurResult(BaseModel):
    blur_score: float
    is_blurry: bool


class PhotoResult(BaseModel):
    id: str
    filename: str
    status: str
    thumbnail_url: str
    original_url: str

    blur_score: float | None = None
    is_blurry: bool | None = None

    eyes_state: str | None = None

    group_id: str | None = None
    is_recommended_keeper: bool | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_record(cls, photo, session_id: str) -> "PhotoResult":
        original_suffix = Path(photo.original_path).suffix or ".jpg"
        return cls(
            id=photo.id,
            filename=photo.filename,
            status=photo.status,
            thumbnail_url=f"/uploads/{session_id}/thumbs/{photo.id}.jpg",
            original_url=f"/uploads/{session_id}/original/{photo.id}{original_suffix}",
            blur_score=photo.blur_score,
            is_blurry=photo.is_blurry,
            eyes_state=photo.eyes_state,
            group_id=photo.group_id,
            is_recommended_keeper=photo.is_recommended_keeper,
        )


class SessionCreateResult(BaseModel):
    session_id: str


class SessionResultsResponse(BaseModel):
    session_id: str
    photos: list[PhotoResult]
