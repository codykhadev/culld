from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app.analysis.grouping import PhotoForGrouping, group_photos
from app.analysis.pipeline import analyze_photo
from app.db import get_db
from app.db_models import PhotoRecord, UploadSessionRecord
from app.models import PhotoResult, SessionCreateResult
from app.storage import decode_image, save_upload

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionCreateResult)
def create_session(db: Session = Depends(get_db)) -> SessionCreateResult:
    session = UploadSessionRecord()
    db.add(session)
    db.commit()
    db.refresh(session)
    return SessionCreateResult(session_id=session.id)


@router.post("/{session_id}/photos", response_model=list[PhotoResult])
async def upload_photos(
    session_id: str,
    files: list[UploadFile],
    db: Session = Depends(get_db),
) -> list[PhotoResult]:
    for file in files:
        raw_bytes = await file.read()

        photo = PhotoRecord(
            session_id=session_id,
            filename=file.filename or "unnamed",
            original_path="",
            thumb_path="",
            status="pending",
        )
        db.add(photo)
        db.flush()  # assigns photo.id without committing yet

        try:
            original_path, thumb_path = save_upload(session_id, photo.id, photo.filename, raw_bytes)
            photo.original_path = str(original_path)
            photo.thumb_path = str(thumb_path)

            image = decode_image(raw_bytes)
            analysis = analyze_photo(image)
            photo.blur_score = analysis["blur_score"]
            photo.is_blurry = analysis["is_blurry"]
            photo.eyes_state = analysis["eyes_state"]
            photo.phash = analysis["phash"]
            photo.status = "analyzed"
        except ValueError:
            photo.status = "failed"

        db.commit()

    # Re-group the whole session (not just this request's files) so photos
    # uploaded in separate batches can still be matched into the same burst.
    all_photos = db.query(PhotoRecord).filter(PhotoRecord.session_id == session_id).all()
    analyzed = [p for p in all_photos if p.phash is not None]

    grouping = group_photos(
        [PhotoForGrouping(id=p.id, phash=p.phash, blur_score=p.blur_score, eyes_state=p.eyes_state) for p in analyzed]
    )
    for photo in analyzed:
        result = grouping[photo.id]
        photo.group_id = result.group_id
        photo.is_recommended_keeper = result.is_recommended_keeper
    db.commit()

    for photo in all_photos:
        db.refresh(photo)

    # Return every photo in the session (not just this request's files),
    # since re-grouping can change group_id/keeper on previously uploaded ones too.
    return [PhotoResult.from_record(photo, session_id) for photo in all_photos]
