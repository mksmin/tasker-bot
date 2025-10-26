# import from libs
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.models import User, UserSettings
from database.schemas import UserCreateSchema, UserReadSchema
from database.schemas.user import UserSettingsSchema

from .base import BaseCRUDManager


class UserManager(BaseCRUDManager[User]):
    def __init__(
        self,
        session_maker: async_sessionmaker[AsyncSession],
    ) -> None:
        super().__init__(
            model=User,
            session_maker=session_maker,
        )

    async def create_user(
        self,
        user_data: dict[str, Any],
    ) -> UserReadSchema:
        instance = UserCreateSchema(**user_data)
        exist = await self.exist(field="user_tg", value=instance.user_tg)
        if exist:
            exist_model = await self.get(user_tg=instance.user_tg)
            return UserReadSchema.model_validate(exist_model)

        created_model = await super().create(data=instance)

        return UserReadSchema.model_validate(created_model)

    async def get_user(
        self,
        *,
        id: int | None = None,
        user_tg: int | None = None,
    ) -> UserReadSchema:
        """
        Получить пользователя по id или Telegram ID (user_tg).
        Один из параметров обязательно должен быть передан

        raises:
            ValueError: если параметры не переданы или пользователь не найден
        """

        if id is None and user_tg is None:
            msg_error = "Either 'id' or 'user_tg' must be provided"
            raise ValueError(msg_error)

        filters = {}
        if id is not None:
            filters["id"] = id
        if user_tg is not None:
            filters["user_tg"] = user_tg

        user_model = await self.get(**filters)

        if user_model is None:
            msg_error = "User not found"
            raise ValueError(msg_error)

        return UserReadSchema.model_validate(user_model)

    async def get_user_settings(
        self,
        user_tg: int,
    ) -> UserSettingsSchema:
        async with self.session_maker() as session:
            if not user_tg:
                message = "User TG is required to get user settings"
                raise ValueError(message)
            stmt = select(User).where(User.user_tg == user_tg)
            query = await session.execute(stmt)
            user = query.scalar_one_or_none()

            if not user:
                message = "User not found"
                raise ValueError(message)

            stmt_settings = select(UserSettings).where(UserSettings.user_id == user.id)
            query = await session.execute(stmt_settings)
            user_settings = query.scalar_one_or_none()
            user_settings.user_tg = user.user_tg  # type: ignore[union-attr]
            return UserSettingsSchema.model_validate(user_settings)
