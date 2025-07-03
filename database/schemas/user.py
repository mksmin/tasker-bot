from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from typing import Optional


class UserCreateSchema(BaseModel):
    user_tg: int = Field(..., description="User Telegram ID")
    first_name: str = Field(..., description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    username: Optional[str] = Field(None, description="User username")

    model_config = ConfigDict(from_attributes=True)


class UserReadSchema(UserCreateSchema):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    username: Optional[str] = Field(None, description="User username")

    model_config = ConfigDict(from_attributes=True)
