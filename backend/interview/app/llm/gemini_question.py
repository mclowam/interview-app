from google import genai

from app.llm.exceptions import QuestionGenerationError
from app.schemas.schemas import QA


class GeminiQuestionGenerator:
    def __init__(self, api_key: str, model:str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def generate(self, position: str, level: int, history: list[QA]) -> str:
        prompt = self._build_prompt(position, level, history)

        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
            )
        except Exception as exc:
            raise QuestionGenerationError("Gemini request failed") from exc

        question = (response.text or "").strip()
        if not question:
            raise QuestionGenerationError("Gemini returned an empty response")

        return question

    def _build_prompt(self, position: str,level: int, history:list[QA]) -> str:
        header = (
            f"You are conducting a technical interview for a {position} "
            f"position at level {level}."
        )

        if not history:
            return (
                f"{header}\n"
                "Ask one opening question. "
                "Return only the question text, no numbering or labels."
            )

        asked = "\n".join(
            f"{i}. {qa.question}" for i, qa in enumerate(history, start=1)
        )

        return (
            f"{header}\n"
            f"Questions already asked in this interview:\n{asked}\n"
            "Ask the next question. Do not repeat a topic already covered "
            "unless going deeper is clearly warranted. "
            "Return only the question text, no numbering or labels."
        )