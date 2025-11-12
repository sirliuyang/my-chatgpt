# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
from pydantic import BaseModel
from typing import List, Optional, Literal


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str
    history: List[ChatMessage] = []  # 可选历史（前端可传，可不传）


class ChatChunk(BaseModel):
    content: str
