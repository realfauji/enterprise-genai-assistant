from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.models.user import User
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.api.auth_routes import router as auth_router
from app.api.chat_routes import router as chat_router
from app.api.session_routes import router as session_router
import app.db.init_db


app = FastAPI(title="Enterprise GenAI Platform")


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def health_check():
    return {"status": "Running"}


app.include_router(auth_router)
app.include_router(session_router)
app.include_router(chat_router)