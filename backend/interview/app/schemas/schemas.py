import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TurnCreateSchema(BaseModel):
    question: str


class TurnUpdateSchema(BaseModel):
    answer: Optional[str] = None
    turn_number: Optional[int] = None
    score: Optional[int] = None
    feedback: Optional[str] = None


class TurnResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    interview_id: uuid.UUID
    question: str
    turn_number: int
    answer: Optional[str] = None
    score: Optional[int] = None
    feedback: Optional[str] = None
    created_at: datetime


@dataclass(frozen=True)
class QA:
    question: str
    answer: str


class EvaluationResult(BaseModel):
    score: int
    feedback: str
