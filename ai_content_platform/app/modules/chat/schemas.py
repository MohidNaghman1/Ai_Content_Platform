from ai_content_platform.app.modules.chat.models import Conversation, Message
from sqlalchemy.orm.attributes import instance_state
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime


class MessageBase(BaseModel):
    content: str
    sender: str  # 'user' or 'assistant'


class MessageCreate(MessageBase):
    pass


class MessageOut(MessageBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ConversationBase(BaseModel):
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    pass


class ConversationOut(ConversationBase):
    id: int
    created_at: datetime
    messages: List[MessageOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class TokenUsageOut(BaseModel):
    tokens_used: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Manual ORM → DTO conversion to avoid lazy loading and async bugs


def conversation_to_out(conv: Conversation) -> "ConversationOut":
    # Check if messages was actually loaded; don't guess
    state = instance_state(conv)
    messages = conv.messages if "messages" in state.dict else []

    return ConversationOut(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        messages=[
            MessageOut(
                id=m.id,
                sender=m.sender,
                content=m.content,
                created_at=m.created_at,
            )
            for m in messages
        ],
    )
