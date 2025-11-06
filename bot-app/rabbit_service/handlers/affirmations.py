from typing import Any

from bot.scheduler import scheduler_instance
from crud.crud_service import get_crud_service_with_session
from rabbit_service.handlers.base import BaseHandler
from rabbit_service.schemas.commands import (
    DeleteAffirmationCommand,
    PatchAffirmationsSettingsCommand,
)
from rabbit_service.schemas.queries import GetPaginatedAffirmationsQuery
from rabbit_service.schemas.results import AffirmationsListResult
from schemas.users import UserSettingsUpdateSchema


class GetPaginatedAffirmationsHandler(BaseHandler):
    async def handle(
        self,
        payload: dict[str, Any],
    ) -> AffirmationsListResult:
        try:
            query = GetPaginatedAffirmationsQuery(**payload)
            async with get_crud_service_with_session() as crud_service:  # type: ignore[var-annotated]
                affirmations = await crud_service.affirm.get_paginated_affirmations(
                    user_tg=query.user_tg,
                    limit=query.limit,
                    offset=query.offset,
                )

            return AffirmationsListResult(
                status="success",
                affirmations=affirmations,
            )
        except Exception as e:
            return AffirmationsListResult(
                status="error",
                message=str(e),
            )


class RemoveAffirmationHandler(BaseHandler):
    async def handle(
        self,
        payload: dict[str, Any],
    ) -> None:
        query = DeleteAffirmationCommand(**payload)
        async with get_crud_service_with_session() as crud_service:  # type: ignore[var-annotated]
            await crud_service.affirm.remove_affirmation(
                user_tg=query.user_tg,
                affirm_id=query.affirmation_id,
            )


class PatchAffirmationsSettingsHandler(BaseHandler):
    async def handle(
        self,
        payload: dict[str, Any],
    ) -> Any:
        payload_in = PatchAffirmationsSettingsCommand(**payload)
        query = UserSettingsUpdateSchema.model_validate(payload_in.settings_in)
        async with get_crud_service_with_session() as crud_service:  # type: ignore[var-annotated]
            updated_settings = await crud_service.user.update_user_settings(
                user_tg=payload_in.user_tg,
                settings_in=query,
            )
            if (
                payload_in.settings_in
                and (
                    payload_in.settings_in.send_enable is not None
                    or payload_in.settings_in.send_time is not None
                )
                and updated_settings.send_enable
            ):
                scheduler_instance.add_or_update_job(
                    user_settings=updated_settings,
                )
            else:
                scheduler_instance.remove_job(
                    user_id=updated_settings.user.id,
                )
