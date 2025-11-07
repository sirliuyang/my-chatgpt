# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from src.crud.base import CRUDBase
from src.models.conversation import Conversation
from src.schemas.conversation import ConversationCreate


class CRUDConversation(CRUDBase[Conversation, ConversationCreate]):
    pass


crud_conversation = CRUDConversation(Conversation)
