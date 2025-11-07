# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from src.crud.base import BaseCRUD
from src.models.message import MessageModel
from datetime import datetime, UTC
from typing import List


class CRUDMessage(BaseCRUD[MessageModel]):
    def create(self, conversation_id: int, role: str, content: str) -> MessageModel:
        new_id = max((m['id'] for m in self.data['messages']), default=0) + 1
        message = {
            "id": new_id,
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "timestamp": datetime.now(UTC).isoformat()
        }
        self.data['messages'].append(message)
        self._save_data()
        return MessageModel(
            id=message["id"],
            conversation_id=message["conversation_id"],
            role=message["role"],
            content=message["content"],
            timestamp=datetime.fromisoformat(message["timestamp"])
        )

    def get_by_conversation(self, conversation_id: int) -> List[MessageModel]:
        messages = [m for m in self.data['messages'] if m["conversation_id"] == conversation_id]
        messages.sort(key=lambda m: datetime.fromisoformat(m["timestamp"]))
        return [MessageModel(
            id=m["id"],
            conversation_id=m["conversation_id"],
            role=m["role"],
            content=m["content"],
            timestamp=datetime.fromisoformat(m["timestamp"])
        ) for m in messages]


crud_message = CRUDMessage(MessageModel)


def create_message(conversation_id: int, role: str, content: str):
    return crud_message.create(conversation_id, role, content)


def get_messages_by_conversation(conversation_id: int):
    return crud_message.get_by_conversation(conversation_id)
