from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ai_content_platform.app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # The 'summary' field stores an incremental summary of the conversation.
    # When the number of messages exceeds a threshold (e.g., 15), the first N messages are summarized using an LLM,
    # and the summary is stored here. The 'summary_msg_count' tracks how many messages are included in the summary.
    # As more messages arrive, the summary is extended incrementally, always
    # representing the conversation up to 'summary_msg_count'.
    summary = Column(Text, nullable=True)
    summary_msg_count = Column(Integer, default=0)

    messages = relationship("Message", back_populates="conversation")
    token_usage = relationship("TokenUsage", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class TokenUsage(Base):
    __tablename__ = "token_usage"
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="token_usage")
