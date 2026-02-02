from pydantic import BaseModel, ConfigDict
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
    messages: List[MessageOut] = []

    model_config = ConfigDict(from_attributes=True)


class TokenUsageOut(BaseModel):
    tokens_used: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
