import httpx


class InterviewClient:
    def __init__(self, base_url: str) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=120.0)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def create_interview(self, user_id: str, position: str, level: int) -> dict:
        response = await self._client.post(
            "/api/v1/interview/",
            json={"user_id": user_id, "position": position, "level": level},
        )
        response.raise_for_status()
        return response.json()

    async def create_turn(self, interview_id: str) -> dict:
        response = await self._client.post(f"/api/v1/interview/{interview_id}/turns")
        response.raise_for_status()
        return response.json()

    async def submit_answer(self, turn_id: str, answer: str) -> dict:
        response = await self._client.patch(
            f"/api/v1/interview/turns/{turn_id}",
            json={"answer": answer},
        )
        response.raise_for_status()
        return response.json()

    async def finish_interview(self, interview_id: str) -> dict:
        response = await self._client.patch(
            f"/api/v1/interview/{interview_id}",
            json={"status": "done"},
        )
        response.raise_for_status()
        return response.json()

    async def list_turns(self, interview_id: str) -> list[dict]:
        response = await self._client.get(f"/api/v1/interview/{interview_id}/turns")
        response.raise_for_status()
        return response.json()
