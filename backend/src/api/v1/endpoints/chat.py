# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
# src/api/v1/endpoints/chat.py
import json
from typing import List, AsyncIterable
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.schemas.chat import ChatRequest, ChatMessage
from src.services.openai_service import get_openai_response
from src.crud.crud_conversation import create_conversation, get_conversation
from src.crud.crud_message import create_message, get_messages_by_conversation

router = APIRouter()


class ChatRequest(BaseModel):
    conversation_id: int | None = None  # Optional conversation ID; if None, create new
    history: List[ChatMessage]  # Previous messages in the conversation
    message: str  # New user message


async def stream_response(generator: AsyncIterable[str]):
    async for chunk in generator:
        yield f"data: {json.dumps({'content': chunk})}\n\n"
    yield "data: [DONE]\n\n"


@router.post("/chat")
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    # If no conversation_id, create a new one
    if request.conversation_id is None:
        conversation = create_conversation()
        request.conversation_id = conversation.id
    else:
        # Verify conversation exists
        if get_conversation(request.conversation_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    # Add user message to history and persist it
    user_message = ChatMessage(role="user", content=request.message)
    create_message(request.conversation_id, user_message.role, user_message.content)

    # Prepare full history for AI, including new user message
    full_history = request.history + [user_message]

    # Get streaming response from OpenAI-compatible service
    try:
        response_generator = get_openai_response(full_history)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    # Collect full assistant response for persistence
    full_assistant_content = [""]

    async def wrapped_generator():
        async for chunk in response_generator:
            full_assistant_content[0] += chunk
            yield chunk

    def save_assistant_response():
        create_message(request.conversation_id, "assistant", full_assistant_content[0])

    background_tasks.add_task(save_assistant_response)

    return StreamingResponse(stream_response(wrapped_generator()), media_type="text/event-stream")