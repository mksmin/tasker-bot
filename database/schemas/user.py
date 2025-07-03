from datetime import datetime
from pydantic import BaseModel, Field

from typing import Optional


class UserCreateSchema(BaseModel):
    user_tg: int = Field(..., description="User Telegram ID")
    first_name: str = Field(..., description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    username: Optional[str] = Field(None, description="User username")

    class Config:
        from_attributes = True


class UserReadSchema(UserCreateSchema):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    username: Optional[str] = Field(None, description="User username")

    class Config:
        from_attributes = True
