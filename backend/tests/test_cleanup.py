from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.cleanup import wipe_all_sessions
from app.db import Base
from app.db_models import PhotoRecord, UploadSessionRecord


def _make_test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_wipe_all_sessions_clears_db_and_files(tmp_path):
    db = _make_test_db()

    session = UploadSessionRecord()
    db.add(session)
    db.flush()

    original_dir = tmp_path / session.id / "original"
    original_dir.mkdir(parents=True)
    photo_file = original_dir / "photo.jpg"
    photo_file.write_bytes(b"fake photo bytes")

    db.add(PhotoRecord(session_id=session.id, filename="photo.jpg", original_path=str(photo_file), thumb_path=""))
    db.commit()

    wipe_all_sessions(db, upload_dir=tmp_path)

    assert db.query(UploadSessionRecord).count() == 0
    assert db.query(PhotoRecord).count() == 0
    assert not photo_file.exists()
    assert tmp_path.exists()  # recreated empty, not left missing
