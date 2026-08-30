import asyncio
import logging

from google import genai
from google.genai import errors, types

from app.llm.exceptions import AnswerEvaluationError
from app.schemas.schemas import EvaluationResult

logger = logging.getLogger(__name__)

SCORE_MIN = 1
SCORE_MAX = 10
LEVEL_LABELS = {1: "джуниор", 2: "мидл", 3: "сеньор"}
MAX_ATTEMPTS = 3


class GeminiAnswerEvaluator:
    def __init__(self, api_key: str, model: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def evaluate(
            self, question: str, answer: str, position: str, level: int
    ) -> EvaluationResult:
        prompt = self._build_prompt(question, answer, position, level)
        last_error: Exception | None = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = await self._client.aio.models.generate_content(
                    model=self._model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=EvaluationResult,
                    ),
                )
                last_error = None
                break
            except Exception as exc:
                last_error = exc
                retryable = isinstance(exc, errors.ServerError) and "503" in str(exc)
                if not retryable or attempt == MAX_ATTEMPTS:
                    logger.exception("Gemini answer evaluation failed")
                    raise AnswerEvaluationError("Gemini request failed") from exc
                await asyncio.sleep(attempt)

        if last_error is not None:
            raise AnswerEvaluationError("Gemini request failed") from last_error

        result = response.parsed
        if not isinstance(result, EvaluationResult):
            try:
                result = EvaluationResult.model_validate(result)
            except Exception as exc:
                raise AnswerEvaluationError(
                    "Gemini returned an unparsable response"
                ) from exc

        if not (SCORE_MIN <= result.score <= SCORE_MAX):
            raise AnswerEvaluationError(
                f"Score {result.score} outside allowed range "
                f"{SCORE_MIN}-{SCORE_MAX}"
            )

        return result

    def _build_prompt(
            self, question: str, answer: str, position: str, level: int
    ) -> str:
        grade = LEVEL_LABELS.get(level, str(level))
        return (
            f"Ты оцениваешь ответ кандидата на техническом собеседовании "
            f"на позицию {position}, уровень {grade}. "
            f"Вопрос: {question}\n"
            f"Ответ кандидата: {answer}\n"
            f"Поставь оценку от {SCORE_MIN} до {SCORE_MAX} и дай короткую "
            "конкретную обратную связь: что верно и чего не хватает. "
            "Поле feedback пиши только на русском языке. "
            "Английский допустим лишь в названиях технологий."
        )
