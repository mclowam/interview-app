import uuid
from typing import Protocol, runtime_checkable

from app.schemas.interview import InterviewCreateSchema, InterviewUpdateSchema
from app.schemas.schemas import TurnUpdateSchema, QA


@runtime_checkable
class IInterview(Protocol):
    async def add(self, data: InterviewCreateSchema):
        pass

    async def update(self, interview_id: uuid.UUID, data: InterviewUpdateSchema):
        pass

    async def get_interview(self, user_id: str):
        pass

    async def get_by_id(self, interview_id: uuid.UUID):
        pass


@runtime_checkable
class ITurn(Protocol):
    async def add(
            self,
            interview_id: uuid.UUID,
            question: str,
            turn_number: int,
    ):
        pass

    async def get_turns_by_interview_id(self, interview_id: uuid.UUID):
        pass

    async def get_by_id(self, turn_id: uuid.UUID):
        pass

    async def get_max_turn_number(self, interview_id: uuid.UUID):
        pass

    async def update(self, turn_id: uuid.UUID, data: TurnUpdateSchema):
        pass


@runtime_checkable
class IQuestionGenerator(Protocol):
    async def generate(self, position: str, level: int, history: list[QA]) -> str:
        pass

@runtime_checkable
class IAnswerEvaluator(Protocol):
    pass