# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import logging

from sqlalchemy.orm import Session
from src.models.message import Message
from src.models.conversation import Conversation
from typing import List
from sqlalchemy import select

logger = logging.getLogger(__name__)


def get_messages_by_conversation(db: Session, conv_id: int) -> List[Message]:
    try:
        query = select(Message).where(Message.conversation_id == conv_id).order_by(Message.created_at.asc())
        result = db.execute(query)
        return list(result.scalars().all())
    except Exception as e:
        logger.error(f"Error fetching messages for conversation {conv_id}: {str(e)}")
        raise


def create_message(
        db: Session,
        conv_id: int,
        role: str,
        content: str
) -> Message:
    try:
        # 验证 role 是否有效
        valid_roles = ["user", "assistant", "system"]
        if role not in valid_roles:
            raise ValueError(f"Invalid role '{role}'. Must be one of: {valid_roles}")

        # 验证 conversation 存在
        conv_query = select(Conversation).where(Conversation.id == conv_id)
        conv = db.execute(conv_query).scalar_one_or_none()
        if not conv:
            raise ValueError(f"Conversation {conv_id} not found")

        # 创建消息
        msg = Message(
            conversation_id=conv_id,
            role=role,
            content=content,
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg
    except ValueError as ve:
        logger.error(f"Validation error in create_message: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Error creating message for conversation {conv_id}: {str(e)}")
        db.rollback()
        raise
