from contextvars import ContextVar, Token
from typing import TypedDict, Optional

from database.models import User, UserSettings


class UserContext(TypedDict):
    user: User
    settings: UserSettings


_user_contex: ContextVar[UserContext] = ContextVar('user_context')


def set_user_context(user: User, settings: UserSettings) -> Token[UserContext]:
    token = _user_contex.set({"user": user, "settings": settings})
    return token


def reset_user_context(token: Token[UserContext]) -> None:
    if token:
        _user_contex.reset(token)
    else:
        raise ValueError("Token is None")


def get_user() -> User:
    return _user_contex.get()["user"]


def get_user_settings() -> UserSettings: \
        return _user_contex.get()["settings"]
