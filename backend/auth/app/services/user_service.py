from backend.auth.app.services.user_abc import IUser
from fastapi import HTTPException

class UserService:
    def __init__(self, user: IUser):
        self._user = user

    async def add_user(
            self,
            username:str,
            tg_id:str,
            is_staff:bool
    ):
            if await self._user.exists_by_username(username):
                raise HTTPException(detail="username already exists")

            