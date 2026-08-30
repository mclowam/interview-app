import uuid

from fastapi import HTTPException

from app.llm.exceptions import AnswerEvaluationError, QuestionGenerationError
from app.schemas.interview import InterviewCreateSchema, InterviewUpdateSchema
from app.schemas.schemas import QA, TurnUpdateSchema
from app.services.interview_abc import (
    IAnswerEvaluator,
    IInterview,
    IQuestionGenerator,
    ITurn,
)


class InterviewService:
    def __init__(
            self,
            interview: IInterview,
            turn: ITurn,
            question_generator: IQuestionGenerator,
            answer_evaluator: IAnswerEvaluator,
    ):
        self._interview = interview
        self._turn = turn
        self._question_generator = question_generator
        self._answer_evaluator = answer_evaluator

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

    async def add_turn(self, interview_id: uuid.UUID):
        interview = await self._interview.get_by_id(interview_id)
        if interview is None:
            raise HTTPException(status_code=404, detail="interview not found")
        if interview.level is None:
            raise HTTPException(status_code=409, detail="interview level is not set")
        if interview.status != "active":
            raise HTTPException(status_code=409, detail="interview is not active")

        existing = await self._turn.get_turns_by_interview_id(interview_id)
        history = [
            QA(question=turn.question, answer=turn.answer)
            for turn in sorted(existing, key=lambda item: item.turn_number)
            if turn.answer
        ]

        try:
            question = await self._question_generator.generate(
                position=interview.position,
                level=interview.level,
                history=history,
            )
        except QuestionGenerationError as exc:
            raise HTTPException(
                status_code=502,
                detail="question generation failed",
            ) from exc

        max_turn_number = await self._turn.get_max_turn_number(interview_id)
        turn_number = 1 if max_turn_number is None else max_turn_number + 1

        return await self._turn.add(
            interview_id=interview_id,
            question=question,
            turn_number=turn_number,
        )

    async def get_turns_by_interview_id(self, interview_id: uuid.UUID):
        interview = await self._interview.get_by_id(interview_id)
        if interview is None:
            raise HTTPException(status_code=404, detail="interview not found")
        return await self._turn.get_turns_by_interview_id(interview_id)

    async def get_turn_by_id(self, turn_id: uuid.UUID):
        turn = await self._turn.get_by_id(turn_id)
        if turn is None:
            raise HTTPException(status_code=404, detail="turn not found")
        return turn

    async def update_turn(self, turn_id: uuid.UUID, data: TurnUpdateSchema):
        turn = await self._turn.get_by_id(turn_id)
        if turn is None:
            raise HTTPException(status_code=404, detail="turn not found")

        interview = await self._interview.get_by_id(turn.interview_id)
        if interview is None:
            raise HTTPException(status_code=404, detail="interview not found")
        if interview.level is None:
            raise HTTPException(status_code=409, detail="interview level is not set")
        if interview.status != "active":
            raise HTTPException(status_code=409, detail="interview is not active")

        updated = await self._turn.update(turn_id=turn_id, data=data)
        if updated is None:
            raise HTTPException(status_code=404, detail="turn not found")

        try:
            result = await self._answer_evaluator.evaluate(
                question=updated.question,
                answer=data.answer,
                position=interview.position,
                level=interview.level,
            )
        except AnswerEvaluationError as exc:
            raise HTTPException(
                status_code=502,
                detail="answer evaluation failed",
            ) from exc

        scored = await self._turn.update(
            turn_id=turn_id,
            score=result.score,
            feedback=result.feedback,
        )
        if scored is None:
            raise HTTPException(status_code=404, detail="turn not found")
        return scored
