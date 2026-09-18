from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.db_models import PhotoRecord, UploadSessionRecord
from app.models import PhotoResult, SessionResultsResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/{session_id}/results", response_model=SessionResultsResponse)
def get_results(session_id: str, db: Session = Depends(get_db)) -> SessionResultsResponse:
    session = db.get(UploadSessionRecord, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    photos = db.query(PhotoRecord).filter(PhotoRecord.session_id == session_id).all()

    return SessionResultsResponse(
        session_id=session_id,
        photos=[PhotoResult.from_record(photo, session_id) for photo in photos],
    )
