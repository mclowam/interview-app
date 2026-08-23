import uuid

from pydantic import BaseModel, ConfigDict


class UserCreateSchema(BaseModel):
    username: str
    tg_id: str


class UserResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    tg_id: str

    is_active: bool
    is_staff: bool


