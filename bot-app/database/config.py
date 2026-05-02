from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import UserSettings


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
        key: str | None = None,
        value: Any | None = None,
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
