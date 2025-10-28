from typing import Any

from crud.crud_service import get_crud_service_with_session
from database.schemas.user import UserSettingsSchema
from rabbit_service.handlers.base import BaseHandler
from rabbit_service.schemas.queries import GetUserSettingsQuery


class GetUserSettingsHandler(BaseHandler):
    async def handle(
        self,
        payload: dict[str, Any],
    ) -> UserSettingsSchema:
        query = GetUserSettingsQuery(**payload)
        async with get_crud_service_with_session() as crud_service:  # type: ignore[var-annotated]
            return await crud_service.user.get_user_settings(
                user_tg=query.user_tg,
            )
