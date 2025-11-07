# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
# src/api/v1/endpoints/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from src.db.session import get_db
from src.schemas.chat import ChatRequest
from src.crud import crud_conversation, crud_message
from src.services.ai_service import stream_chat
import json

router = APIRouter()


@router.post("/chat")
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    if not request.conversation_id:
        conv = crud_conversation.create(db, obj_in={})
        request.conversation_id = conv.id

    for msg in request.messages:
        crud_message.create(db, obj_in={"conversation_id": request.conversation_id, "role": msg.role,
                                        "content": msg.content})

    def event_stream():
        full_content = ""
        for chunk in stream_chat([msg.dict() for msg in request.messages]):
            full_content += chunk
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        crud_message.create(db, obj_in={"conversation_id": request.conversation_id, "role": "assistant",
                                        "content": full_content})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
