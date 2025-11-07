# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from fastapi import APIRouter, HTTPException, status
from typing import List
from src.schemas.conversation import ConversationCreate, Conversation
from src.schemas.message import Message
from src.crud.crud_conversation import create_conversation, get_conversations, get_conversation
from src.crud.crud_message import get_messages_by_conversation

router = APIRouter()


@router.post("/conversations", response_model=Conversation, status_code=status.HTTP_201_CREATED)
def create_new_conversation(conversation: ConversationCreate):
    return create_conversation()


@router.get("/conversations", response_model=List[Conversation])
def list_conversations():
    return get_conversations()


@router.get("/conversations/{conversation_id}", response_model=List[Message])
def get_conversation_history(conversation_id: int):
    if get_conversation(conversation_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return get_messages_by_conversation(conversation_id)
