import uuid

from sqlalchemy import select

from app.models.interview import InterviewModel
from app.schemas.interview import InterviewCreateSchema, InterviewUpdateSchema


class InterviewRepository:
    def __init__(self, session):
        self._session = session

    async def add(self, data: InterviewCreateSchema):
        interview = InterviewModel(
            user_id=data.user_id,
            position=data.position,
            level=data.level,
        )

        self._session.add(interview)
        await self._session.commit()
        await self._session.refresh(interview)

        return interview

    async def get_interview(self, user_id: str):
        query = select(InterviewModel).where(InterviewModel.user_id == user_id)
        result = await self._session.execute(query)

        return result.scalars().all()

    async def get_by_id(self, interview_id: uuid.UUID):
        query = select(InterviewModel).where(InterviewModel.id == interview_id)
        result = await self._session.execute(query)

        return result.scalars().first()

    async def update(self, interview_id: uuid.UUID, data: InterviewUpdateSchema):
        interview = await self.get_by_id(interview_id)

        if not interview:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(interview, key, value)

        await self._session.commit()
        await self._session.refresh(interview)

        return interview
