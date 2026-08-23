from fastapi import APIRouter

from app.db.session import SessionDep
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponseSchema
from app.services.user_service import UserService


def get_service(session) -> UserService:
    return UserService(UserRepository(session=session))


api_v1 = APIRouter(prefix="/auth/api/v1")


@api_v1.post("/", response_model=UserResponseSchema)
async def create_user(
    session: SessionDep,
    username: str,
    tg_id: str,
    is_staff: bool = False,
):
    service = get_service(session)
    return await service.add_user(
        username=username,
        tg_id=tg_id,
        is_staff=is_staff,
    )


@api_v1.get("/tg/id", response_model=UserResponseSchema)
async def user_by_tg_id(session: SessionDep, tg_id: str):
    service = get_service(session)
    return await service.get_user_by_tg_id(tg_id=tg_id)
