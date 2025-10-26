from typing import Any

from database.crud import crud_manager
from database.schemas.user import UserSettingsSchema
from rabbit_service.handlers.base import BaseHandler
from rabbit_service.schemas.queries import GetUserSettingsQuery


class GetUserSettingsHandler(BaseHandler):
    async def handle(
        self,
        payload: dict[str, Any],
    ) -> UserSettingsSchema:
        query = GetUserSettingsQuery(**payload)
        return await crud_manager.user.get_user_settings(
            user_tg=query.user_tg,
        )
