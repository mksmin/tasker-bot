from typing import Any

from crud.crud_service import get_crud_service_with_session
from database.crud import crud_manager
from rabbit_service.handlers.base import BaseHandler
from rabbit_service.schemas.commands import DeleteAffirmationCommand
from rabbit_service.schemas.queries import GetPaginatedAffirmationsQuery
from rabbit_service.schemas.results import AffirmationsListResult


class GetPaginatedAffirmationsHandler(BaseHandler):
    async def handle(
        self,
        payload: dict[str, Any],
    ) -> AffirmationsListResult:
        try:
            query = GetPaginatedAffirmationsQuery(**payload)
            affirmations = await crud_manager.task.get_paginated_tasks(
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
        async with get_crud_service_with_session() as crud_service:  # type: CRUDService
            await crud_service.affirm.remove_affirmation(
                user_tg=query.user_tg,
                affirm_id=query.affirmation_id,
            )
