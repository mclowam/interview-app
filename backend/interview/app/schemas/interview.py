import uuid

from pydantic import BaseModel, ConfigDict


class InterviewCreateSchema(BaseModel):
    user_id: str
    position: str
    level: int


class InterviewResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: str
    level: int | None
    position: str
    status: str


class InterviewUpdateSchema(BaseModel):
    level: int | None = None
    position: str | None = None
    status: str | None = None
