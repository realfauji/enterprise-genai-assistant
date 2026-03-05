from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.models.user import User
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.api.auth_routes import router as auth_router
from app.api.chat_routes import router as chat_router
from app.api.session_routes import router as session_router
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import app.db.init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Enterprise GenAI Platform", lifespan=lifespan)
# app = FastAPI(title="Enterprise GenAI Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Later replace with Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "Running"}


app.include_router(auth_router)
app.include_router(session_router)
app.include_router(chat_router)
