from google import genai
from google.genai import types

from app.schemas.schemas import EvaluationResult

SCORE_MIN = 1
SCORE_MAX = 10


class GeminiAnswerEvaluator:
    def __init__(self, api_key: str, model: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def evaluate(
            self, question: str, answer: str, position: str, level: int
    ) -> EvaluationResult:
        prompt = self._build_prompt(question, answer, position, level)
        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=EvaluationResult,
                ),
            )
        except Exception as exc:
            raise AnswerEvaluationError("Gemini request failed") from exc

        result = response.parsed
        if result is None:
            raise AnswerEvaluationError("Gemini returned an unparsable response")

        if not (SCORE_MIN <= result.score <= SCORE_MAX):
            raise AnswerEvaluationError(
                f"Score {result.score} outside allowed range "
                f"{SCORE_MIN}-{SCORE_MAX}"
            )

        return result

    def _build_prompt(
            self, question: str, answer: str, position: str, level: int
    ) -> str:
        return (
            f"You are evaluating a candidate's answer in a technical "
            f"interview for a {position} position at level {level}.\n"
            f"Question: {question}\n"
            f"Candidate's answer: {answer}\n"
            f"Score the answer from {SCORE_MIN} to {SCORE_MAX} and give "
            "brief, specific feedback on what was correct or missing."
        )