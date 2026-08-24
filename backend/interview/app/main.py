from fastapi import FastAPI

from backend.auth.app.routes.auth import api_v1

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "OK"}


app.include_router(api_v1)