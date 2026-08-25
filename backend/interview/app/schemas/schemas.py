import uuid
from pydantic import BaseModel, ConfigDict


class TurnCreateSchema(BaseModel):
    interview_id: uuid.UUID
    question: str
    turn_number: int


class TurnUpdateSchema(BaseModel):
    answer: str | None = None
    turn_number: int | None = None
    score: int | None = None
    feedback: str | None = None


class TurnResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    interview_id: uuid.UUID
    question: str
    turn_number: int
    answer: str
    score: int
    feedback: str
