from aiogram.filters import BaseFilter
from aiogram.types import Message, User, CallbackQuery, InaccessibleMessage


class HasCallbackMessageFilter(BaseFilter):
    async def __call__(
        self,
        callback: CallbackQuery,
    ) -> dict[str, Message | InaccessibleMessage] | bool:
        if not callback.message:
            return False
        return {
            "callback_message": callback.message,
        }


class HasCallbackUserFilter(BaseFilter):
    async def __call__(
        self,
        callback: CallbackQuery,
    ) -> dict[str, User] | bool:
        if not callback.from_user:
            return False
        return {
            "from_user": callback.from_user,
        }
