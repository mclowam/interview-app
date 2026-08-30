import httpx


class AuthClient:
    def __init__(self, base_url: str) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=15.0)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_by_tg_id(self, tg_id: str) -> dict | None:
        response = await self._client.get(f"/api/v1/auth/tg/{tg_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    async def create_user(self, username: str, tg_id: str) -> dict:
        response = await self._client.post(
            "/api/v1/auth/",
            params={"username": username, "tg_id": tg_id},
        )
        if response.status_code == 409:
            response = await self._client.post(
                "/api/v1/auth/",
                params={"username": f"{username}_{tg_id}", "tg_id": tg_id},
            )
        response.raise_for_status()
        return response.json()

    async def get_or_create(self, username: str, tg_id: int) -> dict:
        tg_id_str = str(tg_id)
        user = await self.get_by_tg_id(tg_id_str)
        if user is not None:
            return user
        return await self.create_user(username, tg_id_str)
