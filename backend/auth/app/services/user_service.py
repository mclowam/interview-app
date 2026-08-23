from fastapi import HTTPException

from app.services.user_abc import IUser


class UserService:
    def __init__(self, user: IUser):
        self._user = user

    async def add_user(
        self,
        username: str,
        tg_id: str,
        is_staff: bool,
    ):
        if await self._user.exists_by_username(username):
            raise HTTPException(
                status_code=409,
                detail="username already exists",
            )

        return await self._user.add(
            username=username,
            tg_id=tg_id,
            is_staff=is_staff,
        )

    async def get_user_by_tg_id(self, tg_id: str):
        result = await self._user.get_user_by_tg_id(tg_id=tg_id)
        if result is None:
            raise HTTPException(status_code=404, detail="user not found")
        return result

    async def get_user_by_id(self, id):
        result = await self._user.get_user_by_id(id=id)
        if result is None:
            raise HTTPException(status_code=404, detail="user not found")
        return result

    async def get_user_username(self, username: str):
        result = await self._user.get_user_by_username(username=username)
        if result is None:
            raise HTTPException(status_code=404, detail="user not found")
        return result
