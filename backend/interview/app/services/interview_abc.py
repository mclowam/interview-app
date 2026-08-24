import uuid
from typing import Protocol, runtime_checkable
from app.schemas.interview import InterviewCreateSchema, InterviewUpdateSchema


@runtime_checkable
class IInterview(Protocol):
    async def add(self, data: InterviewCreateSchema):
        pass

    async def update(self, interview_id: uuid.UUID, data: InterviewUpdateSchema):
        pass

    async def get_interview(self, user_id:str):
        pass
