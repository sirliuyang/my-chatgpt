# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.schemas.conversation import ConversationResponse
from src.schemas.message import MessageResponse
from src.crud.crud_conversation import conversation  # 修改为实例调用
from src.crud.crud_message import get_messages_by_conversation
from src.common.auth_bearer import get_current_user  # 假设添加认证依赖
from typing import List, Dict

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=List[ConversationResponse])
def list_conversations(
        db: Session = Depends(get_db),
        current_user: Dict = Depends(get_current_user)  # 添加认证
):
    """列出所有对话（仅当前用户）"""
    return conversation.get_conversations(db, user_id=current_user["user_id"])


@router.get("/{id}", response_model=List[MessageResponse])
def fetch_conversation(
        id: int,
        db: Session = Depends(get_db),
        current_user: Dict = Depends(get_current_user)  # 添加认证
):
    """获取指定对话的消息历史（验证所属用户）"""
    conv = conversation.get_conversation(db, id, user_id=current_user["user_id"])
    if not conv:
        logger.warning(f"Conversation {id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return get_messages_by_conversation(db, id)


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_new_conversation(
        db: Session = Depends(get_db),
        current_user: Dict = Depends(get_current_user)  # 添加认证
):
    """创建新对话（关联当前用户）"""
    return conversation.create_conversation(db, user_id=current_user["user_id"])
