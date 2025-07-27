from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.context import set_user_context, reset_user_context
from config import logger
from database.crud import crud_manager
from database.crud.managers.base import BaseCRUDManager
from database.models import User, UserSettings
from database.schemas import UserCreateSchema


class SettingsRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_settings(self, user_id: int):
        stmt = (
            select(UserSettings)
            .where(UserSettings.user_id == user_id)
        )
        query = await self.session.execute(stmt)
        result = query.scalar_one_or_none()
        return result

    async def set_settings(
            self,
            user_id: int,
    ):
        existing_settings = await self._get_settings(user_id)

        if not existing_settings:
            new_settings = UserSettings(
                user_id=user_id,
            )
            self.session.add(new_settings)
            await self.session.flush()

        await self.session.commit()

    async def get_settings(self, user_id: int):
        if settings := await self._get_settings(user_id):
            logger.info("Got settings for user with id: %s", user_id)
            return settings
        else:
            await self.set_settings(user_id)
            logger.info("Created settings for user with id: %s", user_id)
            return await self._get_settings(user_id)


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable,
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        session = data["session"]
        tg_user = event.from_user
        settings_repo = SettingsRepo(
            session=session
        )

        # Create user if not exists
        user_data = {
            "user_tg": tg_user.id,
            "first_name": tg_user.first_name,
            "last_name": getattr(tg_user, "last_name", None),
            "username": getattr(tg_user, "username", None),
        }

        user = await crud_manager.user.create_user(
            user_data=user_data
        )
        settings = await settings_repo.get_settings(
            user_id=user.id
        )
        token = set_user_context(
            user=user,
            settings=settings,
        )
        try:
            return await handler(event, data)
        finally:
            reset_user_context(token)