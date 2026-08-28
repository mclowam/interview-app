from fastapi import APIRouter

from app.db.session import SessionDep
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponseSchema
from app.services.user_service import UserService


def get_service(session) -> UserService:
    return UserService(UserRepository(session=session))


api_v1 = APIRouter(prefix="/api/v1/auth")


@api_v1.post("/", response_model=UserResponseSchema)
async def create_user(
        session: SessionDep,
        username: str,
        tg_id: str,
):
    service = get_service(session)
    return await service.add_user(
        username=username,
        tg_id=tg_id,
    )


@api_v1.get("/tg/{tg_id}", response_model=UserResponseSchema)
async def user_by_tg_id(session: SessionDep, tg_id: str):
    service = get_service(session)
    return await service.get_user_by_tg_id(tg_id=tg_id)


@api_v1.get("/username/{username}", response_model=UserResponseSchema)
async def user_by_username(session: SessionDep, username: str):
    service = get_service(session)
    return await service.get_user_username(username=username)


@api_v1.get("/users", response_model=list[UserResponseSchema])
async def all_users(session: SessionDep):
    service = get_service(session)
    return await service.get_all_users()

