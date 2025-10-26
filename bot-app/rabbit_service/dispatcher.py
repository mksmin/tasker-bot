import logging
from typing import Any

from rabbit_service.handlers.affirmations import (
    GetPaginatedAffirmationsHandler,
    RemoveAffirmationHandler,
)
from rabbit_service.handlers.base import BaseHandler
from rabbit_service.handlers.user_settings import GetUserSettingsHandler

log = logging.getLogger(__name__)


class CommandDispatcher:
    def __init__(self) -> None:
        self._handlers: dict[str, BaseHandler] = {}

    def register_handler(
        self,
        command_type: str,
        handler: BaseHandler,
    ) -> None:
        self._handlers[command_type] = handler
        log.info("Registered handler for %s", command_type)

    async def dispatch(
        self,
        command_type: str,
        payload: dict[str, Any],
    ) -> Any:
        handler = self._handlers.get(command_type)
        if not handler:
            message = f"No handler registered for {command_type}"
            raise ValueError(message)
        return await handler.handle(payload)


dp = CommandDispatcher()

dp.register_handler("GetPaginatedAffirmations", GetPaginatedAffirmationsHandler())
dp.register_handler("RemoveAffirmation", RemoveAffirmationHandler())
dp.register_handler("GetUserSettings", GetUserSettingsHandler())
