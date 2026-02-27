from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from app.db.base import Base


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    cost = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())