from sqlalchemy.ext.asyncio import AsyncSession

from app_exceptions.exceptions import TaskNotFoundError, UserNotFoundError
from crud.managers import UserManager
from crud.managers.affirmations import AffirmationManager


class AffirmationService:
    def __init__(
        self,
        session: AsyncSession,
        user_manager: UserManager,
    ) -> None:
        self._session = session
        self._manager = AffirmationManager(self._session)
        self.user_manager = user_manager

    async def remove_affirmation(
        self,
        user_tg: int,
        affirm_id: int,
    ) -> None:
        user = await self.user_manager.get_user_by_tg_id(user_tg)

        if not user:
            message_error = "User not found"
            raise UserNotFoundError(message_error)

        result = await self._manager.remove_affirmation(
            user.id,
            affirm_id,
        )

        if not result:
            message_error = "Affirmation not found or already deleted"
            raise TaskNotFoundError(message_error)

        await self._session.commit()
