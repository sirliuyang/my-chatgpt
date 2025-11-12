# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import logging

from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from src.db.base import Base

logger = logging.getLogger(__name__)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # 关系：属于一个用户
    try:
        user = relationship("User", back_populates="conversations")
    except Exception as e:
        logger.error(f"Error creating User relationship: {str(e)}")
        raise

    # 关系：包含多条消息
    try:
        messages = relationship(
            "Message",
            back_populates="conversation",
            cascade="all, delete-orphan",
            passive_deletes=True
        )
    except Exception as e:
        logger.error(f"Error creating Message relationship: {str(e)}")
        raise

    def __repr__(self) -> str:
        return f"<Conversation id={self.id} user_id={self.user_id} created_at={self.created_at}>"
