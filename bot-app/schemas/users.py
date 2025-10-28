from datetime import datetime, time

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


class UserSettingsBaseSchema(BaseModel):
    count_tasks: int
    send_time: time
    send_enable: bool

    model_config = ConfigDict(from_attributes=True)


class UserSettingsWithUserResponseSchema(UserSettingsBaseSchema):
    user: UserResponseSchema


class UserSettingsWithUserReadSchema(UserSettingsBaseSchema):
    user: UserReadSchema


class UserSettingsUpdateSchema(BaseModel):
    """
    Schema for updating user settings
    """

    count_tasks: int | None = None
    send_time: time | None = None
    send_enable: bool | None = None

    model_config = ConfigDict(from_attributes=True)
