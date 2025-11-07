# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from pydantic import BaseModel
from datetime import datetime


class ConversationCreate(BaseModel):
    pass  # Empty for now; can add fields if needed


class ConversationResponse(BaseModel):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
