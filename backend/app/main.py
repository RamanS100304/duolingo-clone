"""FastAPI entry point:  uvicorn app.main:app --reload"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import CORS_ORIGINS, ENABLE_DEV_TOOLS
from .migrate import upgrade_database
from .routers import dev, learner, path, sessions, social
from .seed import seed
from .services.errors import GameError


@asynccontextmanager
async def lifespan(_app: FastAPI):
    upgrade_database()   # alembic upgrade head
    seed()               # sample course + learner on first start (idempotent)
    yield


app = FastAPI(title="Duolingo Clone API", version="2.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(GameError)
async def game_error_handler(_request: Request, exc: GameError):
    return JSONResponse(status_code=exc.status, content={"detail": exc.message, "code": exc.code})


for module in (learner, path, sessions, social):
    app.include_router(module.router, prefix="/api")
if ENABLE_DEV_TOOLS:
    app.include_router(dev.router, prefix="/api")


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
