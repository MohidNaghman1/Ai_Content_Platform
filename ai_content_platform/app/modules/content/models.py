from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Table,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from ai_content_platform.app.database import Base
from sqlalchemy import UniqueConstraint

# Association table for Article <-> Tag
article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    flagged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = relationship("Tag", secondary=article_tags, back_populates="articles")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    articles = relationship("Article", secondary=article_tags, back_populates="tags")
    __table_args__ = (
        UniqueConstraint(
            "name", name="uq_tag_name_case_insensitive", sqlite_on_conflict="IGNORE"
        ),
    )
