import uuid

from hupper import is_active
from sqlalchemy import select

from backend.auth.app.models.user import UserModel
from backend.auth.app.schemas.user import UserCreateSchema


class UserRepository:
    def __init__(self, session):
        self._session = session

    async def add(
            self,
            *,
            username: str,
            tg_id: str,
            is_staff: bool = False
    ) -> UserModel:
        user = UserModel(
            username=username,
            tg_id=tg_id,
            is_staff=is_staff,
            is_active=True
        )

        self._session.add(user)
        await self._session.commit()
        await self._session.refresh()

        return user

    async def get_user_by_username(self, username: str)->UserModel:
        query = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(query)

        return result.scalar_one_or_none()

    async def get_user_by_tg_id(self, tg_id: str) -> UserModel:
        query = select(UserModel).where(UserModel.tg_id == tg_id)
        result = await self._session.execute(query)

        return result.scalar_one_or_none()

    async def get_user_by_id(self, id: uuid.UUID) -> UserModel:
        query = select(UserModel).where(UserModel.id == id)
        result = await self._session.execute(query)

        return result.scalar_one_or_none()

    async def exists_by_username(self, username: str):
        query = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(query)

        return result.scalar_one_or_none()
