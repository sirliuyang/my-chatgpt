# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
# Streaming chat endpoint

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.schemas.chat import ChatRequest
from src.services.ai_service import stream_chat_response
from src.crud.crud_conversation import create_conversation_if_not_exists
from src.crud.crud_message import create_message
from src.core.security import verify_api_key
from typing import Optional

router = APIRouter()


@router.post("/chat", response_model=None)
async def chat(
        request: ChatRequest,
        db: AsyncSession = Depends(get_db),
        api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Streaming chat endpoint.
    Accepts conversation history + new user message.
    Streams assistant response using pydantic-ai Agent with DeepSeek.
    Stores messages in DB.
    """
    # Verify API key (simple auth)
    verify_api_key(api_key)

    # Create or get conversation
    conversation_id = await create_conversation_if_not_exists(db, request.conversation_id)

    # Store user message
    await create_message(db, conversation_id, "user", request.message)

    # Stream response
    try:
        async def generate():
            full_response = ""
            async for chunk in stream_chat_response(request.history + [{"role": "user", "content": request.message}]):
                yield f"data: {chunk}\n\n"
                full_response += chunk
            # Store assistant response after streaming
            await create_message(db, conversation_id, "assistant", full_response)

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
