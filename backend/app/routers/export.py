import io
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.db_models import PhotoRecord

router = APIRouter(prefix="/sessions", tags=["sessions"])


class ExportRequest(BaseModel):
    photo_ids: list[str]


def _unique_filenames(filenames: list[str]) -> list[str]:
    """Two originally-uploaded files can share a filename (e.g. two
    cameras both named a shot IMG_0001.jpg) — dedupe so the zip doesn't
    silently overwrite one with the other."""
    seen_counts: dict[str, int] = {}
    unique: list[str] = []
    for name in filenames:
        count = seen_counts.get(name, 0)
        seen_counts[name] = count + 1
        if count == 0:
            unique.append(name)
        else:
            stem, dot, suffix = name.rpartition(".")
            base, ext = (stem, f".{suffix}") if dot else (name, "")
            unique.append(f"{base} ({count}){ext}")
    return unique


@router.post("/{session_id}/export")
def export_kept_photos(session_id: str, request: ExportRequest, db: Session = Depends(get_db)) -> Response:
    if not request.photo_ids:
        raise HTTPException(status_code=400, detail="No photo IDs provided")

    photos = (
        db.query(PhotoRecord)
        .filter(PhotoRecord.session_id == session_id, PhotoRecord.id.in_(request.photo_ids))
        .all()
    )
    if not photos:
        raise HTTPException(status_code=404, detail="No matching photos found")

    names = _unique_filenames([photo.filename for photo in photos])

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as zip_file:
        for photo, name in zip(photos, names):
            if Path(photo.original_path).exists():
                zip_file.write(photo.original_path, arcname=name)

    return Response(
        content=buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=kept_photos.zip"},
    )
