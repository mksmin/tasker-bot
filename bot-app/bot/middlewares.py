from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from crud.crud_service import CRUDService
from database.db_helper import DatabaseHelper


class CRUDServiceMiddleware(BaseMiddleware):
    def __init__(
        self,
        db_helper: DatabaseHelper,
    ) -> None:
        super().__init__()
        self.db_helper = db_helper

    async def __call__(
        self,
        handler: Callable[
            [TelegramObject, dict[str, Any]],
            Awaitable[Any],
        ],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async for session in self.db_helper.session_getter():
            crud_service = CRUDService(session)
            data["crud_service"] = crud_service
            return await handler(event, data)

        error_message = "No session created in middleware"
        raise RuntimeError(error_message)
