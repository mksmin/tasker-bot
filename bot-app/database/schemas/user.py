from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreateSchema(BaseModel):
    user_tg: int = Field(..., description="User Telegram ID")
    first_name: str = Field(..., description="User first name")
    last_name: str | None = Field(None, description="User last name")
    username: str | None = Field(None, description="User username")

    model_config = ConfigDict(from_attributes=True)


class UserReadSchema(UserCreateSchema):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(BaseModel):
    first_name: str | None = Field(None, description="User first name")
    last_name: str | None = Field(None, description="User last name")
    username: str | None = Field(None, description="User username")

    model_config = ConfigDict(from_attributes=True)
