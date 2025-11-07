# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from sqlalchemy import Column, Integer, DateTime, func
from src.db.base import Base


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
