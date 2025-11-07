# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from src.db.base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), index=True)
    role = Column(String, nullable=False)  # user/assistant
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
