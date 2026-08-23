import uuid
from typing import Protocol, runtime_checkable

from backend.auth.app.schemas.user import UserCreateSchema, UserResponseSchema


@runtime_checkable
class IUser(Protocol):
    async def add(self, data: UserCreateSchema):
        pass

    async def get_user_by_tg_id(self, tg_id:str)-> UserResponseSchema:
        pass

    async def get_user_by_username(self, username:str)-> UserResponseSchema:
        pass

    async def get_user_by_id(self, id: uuid.UUID)->UserResponseSchema:
        pass

    async def exists_by_username(self, username: str):
        pass