import uuid

from sqlalchemy import func, select

from app.models.turn import TurnModel
from app.schemas.schemas import TurnUpdateSchema


class TurnRepository:
    def __init__(self, session):
        self._session = session

    async def add(
            self, interview_id: uuid.UUID,
            question: str,
            turn_number: int
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

    async def get_by_id(self, turn_id: uuid.UUID):
        query = select(TurnModel).where(TurnModel.id == turn_id)
        result = await self._session.execute(query)

        return result.scalars().first()

    async def get_max_turn_number(self, interview_id: uuid.UUID):
        query = select(func.max(TurnModel.turn_number)).where(
            TurnModel.interview_id == interview_id
        )
        result = await self._session.execute(query)

        return result.scalar()

    async def update(self, turn_id: uuid.UUID, data: TurnUpdateSchema):
        turn = await self.get_by_id(turn_id)

        if not turn:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(turn, key, value)

        await self._session.commit()
        await self._session.refresh(turn)

        return turn
