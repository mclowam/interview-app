import uuid

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

    async def get_interview(self, interview_id):
        return self._interview.get_interview(interview_id)

    async def update_interview(self, interview_id:uuid.UUID, data: InterviewUpdateSchema):
        return await self._interview.update(interview_id,data)

