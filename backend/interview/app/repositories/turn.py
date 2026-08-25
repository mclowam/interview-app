import uuid

from sqlalchemy import select

from app.models.turn import TurnModel
from app.schemas.schemas import TurnUpdateSchema


class TurnRepository:
    def __init__(self, session):
        self._session = session

    async def add(
            self, interview_id:uuid.UUID,
            question: str,
            turn_number:int
    ):
        turn = TurnModel(
            interview_id=interview_id,
            question=question,
            turn_number=turn_number
        )

        self._session.add(turn)
        await self._session.commit()
        await self._session.refresh(turn)

        return turn

    async def get_turns_by_interview_id(self, interview_id: uuid.UUID):
        query = select(TurnModel).where(TurnModel.interview_id == interview_id)
        result = await self._session.execute(query)

        return result.scalars().all()

    #какой id принимать, interview_id или turn_id
    # async def update(self, data: TurnUpdateSchema):
