import uuid

from pydantic import BaseModel


class InterviewCreateSchema(BaseModel):
    user_id: str
    position: str

class InterviewResponseSchema(BaseModel):
    id: uuid.UUID
    user_id: str
    level: str
    position: str
    status: str

class InterviewUpdateSchema(BaseModel):
    level: str | None = None
    position: str | None = None
    status: str | None = None

