from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app_exceptions.exceptions import UserAlreadyExistsError
from app_exceptions.exceptions import UserNotFoundError
from crud.managers.users import UserManager
from database import User
from database import UserSettings
from schemas.users import UserCreateSchema
from schemas.users import UserReadSchema
from schemas.users import UserSettingsUpdateSchema
from schemas.users import UserSettingsWithUserReadSchema


class UserService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session
        self._manager = UserManager(self._session)

    async def _create_default_settings(
        self,
        user: User,
    ) -> UserSettings:
        return await self._manager.get_or_create_user_settings(user)

    async def create_user(
        self,
        user_create: UserCreateSchema | dict[str, Any],
    ) -> UserReadSchema:
        if isinstance(user_create, dict):
            user_create = UserCreateSchema(**user_create)

        user_exists = await self._manager.get_user_by_tg_id(user_create.user_tg)
        if user_exists:
            raise UserAlreadyExistsError

        user = await self._manager.create_user(user_create)
        await self._create_default_settings(user)

        await self._session.commit()
        return UserReadSchema.model_validate(user)

    async def get_by_tg_id(
        self,
        user_tg: int,
    ) -> UserReadSchema:
        user_exists = await self._manager.get_user_by_tg_id(user_tg)
        if not user_exists:
            raise UserNotFoundError
        return UserReadSchema.model_validate(user_exists)

    async def get_by_id(
        self,
        user_id: int,
    ) -> UserReadSchema:
        user_exists = await self._manager.get_user_by_id(user_id)
        if not user_exists:
            raise UserNotFoundError
        return UserReadSchema.model_validate(user_exists)

    async def get_all_users(self) -> list[UserReadSchema]:
        users = await self._manager.get_all_users()
        return [UserReadSchema.model_validate(user) for user in users]

    async def get_user_settings(
        self,
        user_tg: int,
    ) -> UserSettingsWithUserReadSchema:
        user = await self._manager.get_user_by_tg_id(user_tg)
        if not user:
            raise UserNotFoundError
        settings = await self._manager.get_or_create_user_settings(user)
        return UserSettingsWithUserReadSchema.model_validate(settings)

    async def update_user_settings(
        self,
        user_tg: int,
        settings_in: UserSettingsUpdateSchema | UserSettingsWithUserReadSchema,
    ) -> UserSettingsWithUserReadSchema:
        user = await self._manager.get_user_by_tg_id(user_tg)
        if not user:
            raise UserNotFoundError

        settings = await self._manager.get_or_create_user_settings(user)
        await self._manager.update_user_settings(
            settings=settings,
            settings_in=settings_in,
        )

        await self._session.commit()
        return UserSettingsWithUserReadSchema.model_validate(settings)
