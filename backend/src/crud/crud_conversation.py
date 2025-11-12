# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select
from src.crud.base import CRUDBase
from src.models.conversation import Conversation
from typing import List, Optional

logger = logging.getLogger(__name__)


class CRUDConversation(CRUDBase[Conversation]):
    def get_conversations(
            self,
            db: Session,
            user_id: Optional[int] = None,  # 支持可选 user_id，兼容原有无认证调用
            skip: int = 0,
            limit: int = 100
    ) -> List[Conversation]:
        try:
            query = select(self.model)
            if user_id is not None:  # 如果提供 user_id，只返回该用户的对话
                query = query.where(Conversation.user_id == user_id)
            query = query.order_by(Conversation.created_at.desc()).offset(skip).limit(limit)
            result = db.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting conversations: {str(e)}")
            raise

    def get_conversation(self, db: Session, conv_id: int, user_id: Optional[int] = None) -> Optional[Conversation]:
        try:
            query = select(self.model).where(self.model.id == conv_id)
            if user_id is not None:  # 验证是否属于用户
                query = query.where(Conversation.user_id == user_id)
            result = db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting conversation with id {conv_id}: {str(e)}")
            raise

    def create_conversation(self, db: Session, user_id: Optional[int] = None) -> Conversation:
        try:
            obj_in = {}
            if user_id is not None:
                obj_in["user_id"] = user_id
            return self.create(db=db, obj_in=obj_in)
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise

    # 兼容原有函数，如果需要
    def create_conversation_if_not_exists(self, db: Session, conv_id: Optional[int],
                                          user_id: Optional[int] = None) -> int:
        try:
            if conv_id is not None:
                conv = self.get_conversation(db, conv_id, user_id=user_id)
                if conv:
                    return conv.id
            return self.create_conversation(db, user_id=user_id).id
        except Exception as e:
            logger.error(f"Error in create_conversation_if_not_exists: {str(e)}")
            raise

    # 保留新方法
    def get_by_user(
            self,
            db: Session,
            *,
            user_id: int,
            skip: int = 0,
            limit: int = 100
    ) -> List[Conversation]:
        try:
            return self.get_conversations(db, user_id=user_id, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Error getting conversations for user {user_id}: {str(e)}")
            raise

    def create_for_user(self, db: Session, *, user_id: int) -> Conversation:
        try:
            return self.create_conversation(db, user_id=user_id)
        except Exception as e:
            logger.error(f"Error creating conversation for user {user_id}: {str(e)}")
            raise


# 实例化
conversation = CRUDConversation(Conversation)
