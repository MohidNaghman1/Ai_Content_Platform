from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagOut(TagBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ArticleBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    tag_names: Optional[List[str]] = []


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    tag_names: Optional[List[str]] = []


class ArticleOut(ArticleBase):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    tags: List[TagOut] = []

    model_config = ConfigDict(from_attributes=True)
