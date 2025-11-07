# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from pydantic import BaseModel
from datetime import datetime


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True
