from aiogram.filters import BaseFilter
from aiogram.types import Message, User


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
