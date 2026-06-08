"""FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, SessionLocal, engine
from .routers import (
    auth,
    chat,
    customers,
    health,
    matches,
    notes,
    notifications,
    team,
    settings as settings_router,
)
from .seed.seed_db import seed_if_empty


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.SEED_ON_STARTUP:
        with SessionLocal() as db:
            seed_if_empty(db)
    yield


app = FastAPI(title="Saathiya Matchmaker API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (health, auth, customers, notes, matches, team, notifications, settings_router, chat):
    app.include_router(module.router, prefix="/api")
