from fastapi import FastAPI

from app.routes.auth import api_v1

app = FastAPI(title="auth")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_v1)