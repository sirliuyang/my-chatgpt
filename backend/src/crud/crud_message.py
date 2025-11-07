# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from sqlalchemy.orm import Session
from src.crud.base import CRUDBase
from src.models.message import Message
from src.schemas.message import MessageCreate


class CRUDMessage(CRUDBase[Message, MessageCreate]):
    def get_by_conversation(self, db: Session, conversation_id: int):
        return db.query(self.model).filter(self.model.conversation_id == conversation_id).all()


crud_message = CRUDMessage(Message)
