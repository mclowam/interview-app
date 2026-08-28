import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.base import Base


class TurnModel(Base):
    __tablename__ = "turns"
    __table_args__ = (
        UniqueConstraint(
            "interview_id",
            "turn_number",
            name="uq_turns_interview_id_turn_number",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    interview_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False
    )
    question: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    answer: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    turn_number: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    score: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    feedback: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
