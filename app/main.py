from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await init_db()
    yield
    # shutdown (пока ничего)

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def receive_webhook(request: Request):
    raw = await request.body()
    print(raw)
