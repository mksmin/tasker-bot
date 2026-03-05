from aiogram.filters import BaseFilter
from aiogram.filters import Filter
from aiogram.types import Message
from aiogram.types import User

from config import settings


class HasUserFilter(BaseFilter):
    async def __call__(
        self,
        message: Message,
    ) -> dict[str, User] | bool:
        if not message.from_user:
            return False
        return {
            "from_user": message.from_user,
        }


class RootPermissionFilter(Filter):
    async def __call__(
        self,
        message: Message,
    ) -> bool:
        if message.from_user:
            return message.from_user.id == settings.bot.owner_tg_id
        return False
