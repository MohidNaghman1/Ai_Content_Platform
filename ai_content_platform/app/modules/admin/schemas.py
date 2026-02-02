# Schemas for admin dashboard endpoints
from pydantic import BaseModel
from typing import List, Optional


class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool


class FlaggedContent(BaseModel):
    id: int
    content: str
    flagged_reason: str
    reviewed: bool


class AnalyticsStats(BaseModel):
    users: int
    articles: int
    ai_usage: int


class SystemHealth(BaseModel):
    status: str
    details: Optional[str] = None
