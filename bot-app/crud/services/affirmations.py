from sqlalchemy.ext.asyncio import AsyncSession

from app_exceptions.exceptions import (
    TaskNotFoundError,
    UserHasNoTasksError,
    UserNotFoundError,
)
from crud.managers import UserManager
from crud.managers.affirmations import AffirmationManager
from database import UserSettings
from schemas.affirmations import AffirmationReadSchema


class AffirmationService:
    def __init__(
        self,
        session: AsyncSession,
        user_manager: UserManager,
    ) -> None:
        self._session = session
        self._manager = AffirmationManager(self._session)
        self.user_manager = user_manager

    async def _get_user_with_settings(
        self,
        user_tg: int,
    ) -> UserSettings:
        user = await self.user_manager.get_user_by_tg_id(user_tg)
        if not user:
            message_error = f"User with tg_id={user_tg} not found"
            raise UserNotFoundError(message_error)

        return await self.user_manager.get_or_create_user_settings(user)

    async def create_affirmation(
        self,
        user_tg: int,
        text: str,
    ) -> AffirmationReadSchema:
        settings_with_user = await self._get_user_with_settings(user_tg)
        affirmation = await self._manager.create_affirmation(
            user_id=settings_with_user.user_id,
            text=text,
        )
        await self._session.commit()

        return AffirmationReadSchema.model_validate(affirmation)

    async def get_paginated_affirmations(
        self,
        user_tg: int,
        offset: int,
        limit: int,
    ) -> list[AffirmationReadSchema]:
        settings_with_user = await self._get_user_with_settings(user_tg)
        list_affirmations = await self._manager.get_paginated_affirmations(
            user_id=settings_with_user.user_id,
            offset=offset,
            limit=limit,
        )
        if not list_affirmations:
            message_error = f"No affirmations found for user={user_tg}"
            raise TaskNotFoundError(message_error)

        return [
            AffirmationReadSchema.model_validate(task) for task in list_affirmations
        ]

    async def get_random_affirmations(
        self,
        user_tg: int,
        count: int | None = None,
    ) -> list[AffirmationReadSchema]:
        settings_with_user = await self._get_user_with_settings(user_tg)
        list_affirmations = await self._manager.get_random_affirmation(
            settings_with_user.user_id,
            count=count if count else settings_with_user.count_tasks,
        )
        if not list_affirmations:
            message_error = f"No affirmations found for user={user_tg}"
            raise UserHasNoTasksError(message_error)

        return [
            AffirmationReadSchema.model_validate(task) for task in list_affirmations
        ]

    async def remove_affirmation(
        self,
        user_tg: int,
        affirm_id: int,
    ) -> None:
        user = await self._get_user_with_settings(user_tg)
        result = await self._manager.remove_affirmation(
            user.user_id,
            affirm_id,
        )
        if not result:
            message_error = (
                f"Affirmation {affirm_id} not found "
                f"or already deleted for user={user_tg}"
            )
            raise TaskNotFoundError(message_error)

        await self._session.commit()
