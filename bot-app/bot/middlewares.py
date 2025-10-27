from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app_exceptions.exceptions import UserAlreadyExistsError
from crud.crud_service import CRUDService
from database.db_helper import DatabaseHelper, db_helper
from schemas.users import UserResponseSchema


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


class CreateUserInjectMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if data.get("handler") and data["handler"].flags.get("create_user"):
            async for session in db_helper.session_getter():
                crud_service = CRUDService(session)
                user_create = {
                    "user_tg": event.from_user.id,  # type: ignore[attr-defined]
                    "first_name": event.from_user.first_name,  # type: ignore[attr-defined]
                    "last_name": event.from_user.last_name,  # type: ignore[attr-defined]
                    "username": event.from_user.username,  # type: ignore[attr-defined]
                }
                try:
                    user = await crud_service.user.create_user(user_create)
                except UserAlreadyExistsError:
                    user = await crud_service.user.get_by_tg_id(event.from_user.id)  # type: ignore[attr-defined]
                data["user_db"] = UserResponseSchema.model_validate(user)

        return await handler(event, data)


class GetUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if data.get("handler") and data["handler"].flags.get("user"):
            async for session in db_helper.session_getter():
                crud_service = CRUDService(session)
                user = await crud_service.user.get_by_tg_id(event.from_user.id)  # type: ignore[attr-defined]
                data["user_db"] = UserResponseSchema.model_validate(user)

        return await handler(event, data)


class GetUserSettingsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if data.get("handler") and data["handler"].flags.get("user_settings"):
            async for session in db_helper.session_getter():
                crud_service = CRUDService(session)
                data["user_settings_db"] = await crud_service.user.get_user_settings(
                    event.from_user.id,  # type: ignore[attr-defined]
                )

        return await handler(event, data)
