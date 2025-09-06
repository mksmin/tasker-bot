from contextvars import ContextVar
from typing import Any, Awaitable, Callable, Coroutine, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# import from modules
from config.config import settings

from .models import UserSettings

engine = create_async_engine(url=str(settings.db.url), echo=False)
async_session = async_sessionmaker(bind=engine, expire_on_commit=True)


class SettingsRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: int) -> UserSettings | None:
        query = await self.session.execute(
            select(UserSettings).where(UserSettings.user_id == user_id),
        )
        return query.scalar_one_or_none()

    async def set(
        self,
        user_id: int,
        key: Optional[str] = None,
        value: Optional[Any] = None,
    ) -> None:
        existing_settings = await self.get(user_id)

        if not existing_settings:
            new_settings = UserSettings(user_id=user_id)
            self.session.add(new_settings)
            await self.session.flush()

            existing_settings = new_settings

        if key:
            setattr(existing_settings, key, value)
        await self.session.commit()


# ContextVar
user_settings_ctx: ContextVar[SettingsRepo] = ContextVar("user_settings")


# Middleware
class DbSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with async_session() as session:
            data["session"] = session
            return await handler(event, data)


class SettingsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        session: AsyncSession = data["session"]
        repo = SettingsRepo(session)
        token = user_settings_ctx.set(repo)
        try:
            return await handler(event, data)
        finally:
            user_settings_ctx.reset(token)
