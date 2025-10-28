from typing import Any

from crud.crud_service import get_crud_service_with_session
from rabbit_service.handlers.base import BaseHandler
from rabbit_service.schemas.queries import GetUserSettingsQuery
from schemas.users import UserSettingsWithUserReadSchema


class GetUserSettingsHandler(BaseHandler):
    async def handle(
        self,
        payload: dict[str, Any],
    ) -> UserSettingsWithUserReadSchema:
        query = GetUserSettingsQuery(**payload)
        async with get_crud_service_with_session() as crud_service:  # type: ignore[var-annotated]
            return await crud_service.user.get_user_settings(  # type: ignore[no-any-return]
                user_tg=query.user_tg,
            )
