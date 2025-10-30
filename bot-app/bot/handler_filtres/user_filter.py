from aiogram.filters import BaseFilter, Filter
from aiogram.types import Message, User

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
        return message.from_user.id == settings.bot.owner_tg_id
