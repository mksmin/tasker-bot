from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    user_tg: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(UserBase):
    """
    Schema for creating a new user
    """


class UserResponseSchema(UserBase):
    """
    Schema for returning a user
    """


class UserReadSchema(UserBase):
    """
    Schema for reading a user in app
    """

    id: int
    created_at: datetime
