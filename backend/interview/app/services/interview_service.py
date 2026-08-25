import uuid

from fastapi import HTTPException

from app.schemas.interview import InterviewCreateSchema, InterviewUpdateSchema
from app.services.interview_abc import IInterview


class InterviewService:
    def __init__(
            self,
            interview: IInterview
    ):
        self._interview = interview

    async def add_interview(self, data: InterviewCreateSchema):
        return await self._interview.add(data)

    async def get_interview(self, user_id: str):
        return await self._interview.get_interview(user_id)

    async def get_interview_by_id(self, interview_id: uuid.UUID):
        interview = await self._interview.get_by_id(interview_id)
        if interview is None:
            raise HTTPException(status_code=404, detail="interview not found")
        return interview

    async def update_interview(self, interview_id: uuid.UUID, data: InterviewUpdateSchema):
        interview = await self._interview.update(interview_id, data)
        if interview is None:
            raise HTTPException(status_code=404, detail="interview not found")
        return interview
