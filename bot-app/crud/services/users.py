from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app_exceptions.exceptions import UserAlreadyExistsError, UserNotFoundError
from crud.managers.users import UserManager
from schemas.users import UserCreateSchema, UserReadSchema


class UserService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session
        self._manager = UserManager(self._session)

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
