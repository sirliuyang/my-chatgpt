# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.db.session import get_db
from src.schemas.conversation import ConversationCreate, ConversationOut
from src.crud import crud_conversation

router = APIRouter()


@router.post("/conversations", response_model=ConversationOut)
def create_conversation(conversation: ConversationCreate, db: Session = Depends(get_db)):
    return crud_conversation.create(db, obj_in=conversation)


@router.get("/conversations", response_model=List[ConversationOut])
def list_conversations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_conversation.get_multi(db, skip=skip, limit=limit)


@router.get("/conversations/{id}", response_model=ConversationOut)
def get_conversation(id: int, db: Session = Depends(get_db)):
    conv = crud_conversation.get(db, id=id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv
