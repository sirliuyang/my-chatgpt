# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import logging

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from src.db.base import Base

logger = logging.getLogger(__name__)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # 反向关系
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self) -> str:
        try:
            return f"<Message id={self.id} role={self.role} conversation_id={self.conversation_id}>"
        except Exception as e:
            logger.error(f"Error in Message.__repr__: {str(e)}")
            return "<Message: representation error>"
