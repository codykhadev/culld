import shutil
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import UPLOAD_DIR
from app.db import SessionLocal
from app.db_models import PhotoRecord, UploadSessionRecord


def wipe_all_sessions(db: Session, upload_dir: Path = UPLOAD_DIR) -> None:
    """Deletes every session, photo row, and uploaded file. This is a
    single-user local tool with no per-session expiration UI, so a full
    wipe on shutdown is simpler than tracking individual session ages."""
    db.query(PhotoRecord).delete()
    db.query(UploadSessionRecord).delete()
    db.commit()

    if upload_dir.exists():
        shutil.rmtree(upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)


def wipe_all_sessions_on_shutdown() -> None:
    db = SessionLocal()
    try:
        wipe_all_sessions(db)
    finally:
        db.close()
