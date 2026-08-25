import uuid
from typing import Protocol, runtime_checkable

from app.schemas.schemas import TurnUpdateSchema


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

    async def update(self,turn_id: uuid.UUID, data: TurnUpdateSchema):
        pass
