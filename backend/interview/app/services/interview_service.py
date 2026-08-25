import uuid

from fastapi import HTTPException

from app.schemas.interview import InterviewCreateSchema, InterviewUpdateSchema
from app.schemas.schemas import TurnCreateSchema
from app.services.interview_abc import IInterview
from app.services.turn_abc import ITurn


class InterviewService:
    def __init__(
            self,
            interview: IInterview,
            turn: ITurn
    ):
        self._interview = interview
        self._turn = turn

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

    async def add_turn(self, data: TurnCreateSchema):
        return await self._turn.add(
            interview_id=data.interview_id,
            question=data.question,
            turn_number=data.turn_number
        )

    async def get_turns_by_interview_id(self, interview_id: uuid.UUID):
        turns = await self._turn.get_turns_by_interview_id(interview_id)
        if turns is None:
            raise HTTPException(status_code=404, detail="turns not found")
        return turns
