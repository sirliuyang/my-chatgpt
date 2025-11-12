# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
from .message import MessageResponse


class ConversationBase(BaseModel):
    pass


class ConversationCreate(ConversationBase):
    pass


class ConversationResponse(ConversationBase):
    id: int = Field(..., description="对话ID")
    user_id: int = Field(..., description="所属用户ID")
    created_at: datetime = Field(..., description="创建时间")
    messages: List[MessageResponse] = Field(default=[], description="消息列表")

    class Config:
        from_attributes = True
