# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from typing import List

from src.crud.base import BaseCRUD
from src.models.conversation import ConversationModel
from datetime import datetime, UTC


class CRUDConversation(BaseCRUD[ConversationModel]):
    def create(self) -> ConversationModel:
        new_id = max((c['id'] for c in self.data['conversations']), default=0) + 1
        conversation = {"id": new_id, "created_at": datetime.now(UTC).isoformat()}
        self.data['conversations'].append(conversation)
        self._save_data()
        return ConversationModel(id=conversation["id"], created_at=datetime.fromisoformat(conversation["created_at"]))

    def get_all(self) -> List[ConversationModel]:
        return [ConversationModel(id=c["id"], created_at=datetime.fromisoformat(c["created_at"])) for c in
                self.data['conversations']]

    def get(self, conversation_id: int) -> ConversationModel | None:
        for c in self.data['conversations']:
            if c["id"] == conversation_id:
                return ConversationModel(id=c["id"], created_at=datetime.fromisoformat(c["created_at"]))
        return None


crud_conversation = CRUDConversation(ConversationModel)


def create_conversation():
    return crud_conversation.create()


def get_conversations():
    return crud_conversation.get_all()


def get_conversation(conversation_id: int):
    return crud_conversation.get(conversation_id)
