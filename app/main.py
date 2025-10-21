from fastapi import FastAPI

from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from core.db import engine
from core.config import settings
from model import *

from api.main import router

def initialise_db():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifeSpan(app: FastAPI):
    initialise_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifeSpan
)

app.include_router(router)