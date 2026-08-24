import uuid
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from sqlalchemy import String,Integer

class InterviewModel(Base):
    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(
        String(200), index=True, nullable=False
    )
    level: Mapped[int] = mapped_column(
        Integer,
    )
    position: Mapped[str] = mapped_column(
        String(500)
    )
    status: Mapped[str] = mapped_column(
        String(200), default="active"
    )