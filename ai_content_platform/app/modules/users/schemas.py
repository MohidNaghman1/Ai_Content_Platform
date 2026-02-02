"""
Pydantic schemas for user input/output.
Defines request/response models for user endpoints in the user management module.
Includes schemas for registration, output, and profile update.
"""

from pydantic import BaseModel, ConfigDict, constr
from typing import Optional, Annotated, Literal

UsernameStr = Annotated[str, constr(min_length=3, max_length=50)]
PasswordStr = Annotated[str, constr(min_length=6)]


class UserBase(BaseModel):
    """
    Base user schema with username and role.
    Used as a base for other user-related schemas.
    """

    username: UsernameStr
    role: Literal["admin", "creator", "viewer"] = "viewer"


class UserCreate(UserBase):
    """
    Schema for user registration input.
    Includes password and email fields.
    """

    password: PasswordStr
    email: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    avatar: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """
    Schema for updating user profile.
    All fields are optional for partial updates.
    """

    username: Optional[str]
    password: Optional[str]
    email: Optional[str]
    avatar: Optional[str]
