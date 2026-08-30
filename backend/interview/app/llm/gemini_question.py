import asyncio
import logging

from google import genai
from google.genai import errors

from app.llm.exceptions import QuestionGenerationError
from app.schemas.schemas import QA

logger = logging.getLogger(__name__)

LEVEL_LABELS = {1: "джуниор", 2: "мидл", 3: "сеньор"}
MAX_ATTEMPTS = 3


class GeminiQuestionGenerator:
    def __init__(self, api_key: str, model: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def generate(self, position: str, level: int, history: list[QA]) -> str:
        prompt = self._build_prompt(position, level, history)
        last_error: Exception | None = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = await self._client.aio.models.generate_content(
                    model=self._model,
                    contents=prompt,
                )
                question = (response.text or "").strip()
                if question:
                    return question
                last_error = QuestionGenerationError("Gemini returned an empty response")
            except Exception as exc:
                last_error = exc
                retryable = isinstance(exc, errors.ServerError) and "503" in str(exc)
                if not retryable or attempt == MAX_ATTEMPTS:
                    logger.exception("Gemini question generation failed")
                    raise QuestionGenerationError("Gemini request failed") from exc
                await asyncio.sleep(attempt)

        raise QuestionGenerationError("Gemini request failed") from last_error

    def _build_prompt(self, position: str, level: int, history: list[QA]) -> str:
        grade = LEVEL_LABELS.get(level, str(level))
        header = (
            f"Ты проводишь техническое собеседование на позицию {position}, "
            f"уровень {grade}. "
            "Весь текст пиши только на русском языке. "
            "Английский допустим лишь в названиях технологий. "
            "Верни только текст одного вопроса, без нумерации и подписей."
        )

        if not history:
            return f"{header}\nЗадай один вступительный вопрос."

        asked = "\n".join(
            f"{i}. Вопрос: {qa.question}\n   Ответ: {qa.answer}"
            for i, qa in enumerate(history, start=1)
        )
        return (
            f"{header}\n"
            f"Предыдущие вопросы и ответы:\n{asked}\n"
            "Задай следующий вопрос. Не повторяй уже закрытую тему, "
            "если нет смысла углубиться."
        )
