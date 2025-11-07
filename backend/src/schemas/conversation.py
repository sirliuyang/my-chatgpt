# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from pydantic import BaseModel
from datetime import datetime
from typing import List


class ConversationCreate(BaseModel):
    pass


class ConversationOut(BaseModel):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
