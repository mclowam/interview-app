import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Integer, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.base import Base


class TurnModel(Base):
    __tablename__ = "turns"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    interview_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False
    )
    question: Mapped[str] = mapped_column(
        String(500), nullable=False
    )
    answer: Mapped[str] = mapped_column(
        String(500), nullable=True
    )
    turn_number: Mapped[int] = mapped_column(
        Integer, nullable=True
    )
    score: Mapped[int] = mapped_column(
        Integer, nullable=True
    )
    feedback: Mapped[str] = mapped_column(
        String(500), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
