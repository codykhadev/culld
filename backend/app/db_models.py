import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class UploadSessionRecord(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    photos: Mapped[list["PhotoRecord"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class PhotoRecord(Base):
    __tablename__ = "photos"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"))
    filename: Mapped[str] = mapped_column(String)
    original_path: Mapped[str] = mapped_column(String)
    thumb_path: Mapped[str] = mapped_column(String)

    status: Mapped[str] = mapped_column(String, default="pending")  # pending | analyzed | failed

    blur_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_blurry: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    eyes_state: Mapped[str | None] = mapped_column(String, nullable=True)

    phash: Mapped[str | None] = mapped_column(String, nullable=True)
    group_id: Mapped[str | None] = mapped_column(String, nullable=True)
    is_recommended_keeper: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    session: Mapped["UploadSessionRecord"] = relationship(back_populates="photos")
