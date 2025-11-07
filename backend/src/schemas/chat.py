# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from pydantic import BaseModel
from typing import List, Dict, Optional


class ChatRequest(BaseModel):
    conversation_id: Optional[int]  # Optional; auto-create if missing
    message: str
    history: List[Dict[str, str]]  # [{"role": "user/assistant", "content": "..."}]


class ChatResponse(BaseModel):
    # Not used directly due to streaming
    pass
