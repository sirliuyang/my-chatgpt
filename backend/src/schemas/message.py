# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, ForwardRef

# 前向引用（避免循环导入）
ConversationResponse = ForwardRef("ConversationResponse")


class MessageBase(BaseModel):
    role: str = Field(..., description="消息角色: 'user' 或 'assistant'")
    content: str = Field(..., description="消息内容")


class MessageCreate(MessageBase):
    conversation_id: int = Field(..., description="所属对话ID")


class MessageInDB(MessageBase):
    id: int = Field(..., description="消息ID")
    conversation_id: int = Field(..., description="所属对话ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class MessageResponse(MessageBase):
    id: int = Field(..., description="消息ID")
    conversation_id: int = Field(..., description="所属对话ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


# 用于嵌套返回（可选）
class MessageWithConversation(MessageResponse):
    conversation: Optional[ConversationResponse] = Field(None, description="所属对话")

    class Config:
        from_attributes = True
