# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from src.models.conversation import Conversation
from src.crud.base import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession

class CRUDConversation(CRUDBase[Conversation]):
    async def create_if_not_exists(self, db: AsyncSession, conversation_id: int | None) -> int:
        if conversation_id:
            conv = await self.get(db, conversation_id)
            if conv:
                return conv.id
        new_conv = await self.create(db, {})
        return new_conv.id

get_conversations = CRUDConversation(Conversation).get_multi
get_conversation = CRUDConversation(Conversation).get
create_conversation = CRUDConversation(Conversation).create
create_conversation_if_not_exists = CRUDConversation(Conversation).create_if_not_exists