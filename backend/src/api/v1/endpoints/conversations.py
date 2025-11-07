# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.schemas.conversation import ConversationCreate, ConversationResponse
from src.schemas.message import MessageResponse
from src.crud.crud_conversation import get_conversations, get_conversation, create_conversation
from src.crud.crud_message import get_messages_by_conversation
from typing import List

router = APIRouter()

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(db: AsyncSession = Depends(get_db)):
    """List all conversations."""
    return await get_conversations(db)

@router.get("/conversations/{id}", response_model=List[MessageResponse])
async def fetch_conversation(id: int, db: AsyncSession = Depends(get_db)):
    """Fetch message history for a conversation."""
    conversation = await get_conversation(db, id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return await get_messages_by_conversation(db, id)

@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_new_conversation(conversation: ConversationCreate, db: AsyncSession = Depends(get_db)):
    """Create a new conversation."""
    return await create_conversation(db, conversation)