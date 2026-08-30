import asyncio
import logging

import httpx
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.clients.auth_client import AuthClient
from app.clients.interview_client import InterviewClient
from app.config import settings
from app.handlers.interview import router

logger = logging.getLogger(__name__)


async def wait_http(url: str) -> None:
    async with httpx.AsyncClient(timeout=2.0) as client:
        for _ in range(40):
            try:
                response = await client.get(url)
                if response.status_code < 500:
                    return
            except httpx.RequestError:
                pass
            await asyncio.sleep(1)
    raise RuntimeError(f"service not ready: {url}")


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    await wait_http(f"{settings.auth_service_url.rstrip('/')}/health")
    await wait_http(f"{settings.interview_service_url.rstrip('/')}/health")

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    auth_client = AuthClient(settings.auth_service_url)
    interview_client = InterviewClient(settings.interview_service_url)
    dp["auth_client"] = auth_client
    dp["interview_client"] = interview_client

    try:
        await dp.start_polling(bot)
    finally:
        await auth_client.aclose()
        await interview_client.aclose()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
