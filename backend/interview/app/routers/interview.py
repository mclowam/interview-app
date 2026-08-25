import uuid

from fastapi import APIRouter

from app.db.session import SessionDep
from app.repositories.interview import InterviewRepository
from app.schemas.interview import (
    InterviewCreateSchema,
    InterviewResponseSchema,
    InterviewUpdateSchema,
)
from app.services.interview_service import InterviewService


def get_service(session) -> InterviewService:
    return InterviewService(
        InterviewRepository(session)
    )


api_v1 = APIRouter(
    prefix="/interview/api/v1"
)


@api_v1.post("/", response_model=InterviewResponseSchema)
async def create_interview(session: SessionDep, data: InterviewCreateSchema):
    service = get_service(session)
    return await service.add_interview(data)


@api_v1.get("/user/{user_id}", response_model=list[InterviewResponseSchema])
async def get_interviews_by_user(session: SessionDep, user_id: str):
    service = get_service(session)
    return await service.get_interview(user_id)


@api_v1.get("/{interview_id}", response_model=InterviewResponseSchema)
async def get_interview(session: SessionDep, interview_id: uuid.UUID):
    service = get_service(session)
    return await service.get_interview_by_id(interview_id)


@api_v1.patch("/{interview_id}", response_model=InterviewResponseSchema)
async def update_interview(
        session: SessionDep,
        interview_id: uuid.UUID,
        data: InterviewUpdateSchema,
):
    service = get_service(session)
    return await service.update_interview(interview_id=interview_id, data=data)
