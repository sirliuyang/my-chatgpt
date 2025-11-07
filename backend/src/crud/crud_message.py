# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
# CRUD for Message

from src.models.message import Message
from src.crud.base import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List


class CRUDMessage(CRUDBase[Message]):
    async def get_by_conversation(self, db: AsyncSession, conversation_id: int) -> List[Message]:
        query = select(self.model).where(self.model.conversation_id == conversation_id).order_by(self.model.timestamp)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create_message(self, db: AsyncSession, conversation_id: int, role: str, content: str) -> Message:
        return await self.create(db, {"conversation_id": conversation_id, "role": role, "content": content})


get_messages_by_conversation = CRUDMessage(Message).get_by_conversation
create_message = CRUDMessage(Message).create_message
