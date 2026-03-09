"""
Run this ONCE after first deployment to create all DB tables.
Usage: python init_tables.py
"""
import asyncio
from app.db.session import engine
from app.db.base import Base

# Import all models so SQLAlchemy knows about them
import app.models.user
import app.models.chat_session
import app.models.chat_message
import app.models.usage_log


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ All tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())
