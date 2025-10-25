import logging
from abc import ABC, abstractmethod
from typing import Any

from faststream.rabbit import RabbitBroker, RabbitMessage
from pydantic import BaseModel

from config import settings
from database.crud import crud_manager
from database.schemas import TaskReadSchema

broker = RabbitBroker(settings.rabbit.url)

log = logging.getLogger(__name__)


class BaseCommand(BaseModel):
    """Базовая команда"""


class BaseQuery(BaseModel):
    """Базовый запрос (для RPC)"""


class BaseResult(BaseModel):
    status: str
    message: str | None = None


class CreateAffirmationCommand(BaseCommand):
    user_tg: int
    affirmation_text: str


class DeleteAffirmationCommand(BaseCommand):
    user_tg: int
    affirmation_id: int


class GetAffirmationQuery(BaseQuery):
    affirmation_id: int


class GetUserAffirmationsQuery(BaseQuery):
    user_tg: int
    count: int = 10


class GetPaginatedAffirmationsQuery(BaseQuery):
    user_tg: int
    limit: int
    offset: int


class AffirmationResult(BaseResult):
    affirmation: TaskReadSchema | None = None


class AffirmationsListResult(BaseResult):
    affirmations: list[TaskReadSchema] = []


class BaseHandler(ABC):
    @abstractmethod
    async def handle(
        self,
        payload: dict[str, Any],
    ) -> Any: ...


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


# fire-and-forget
@broker.subscriber("cmd.affirmations")
async def handle_commands(
    msg: dict[str, Any],
    message: RabbitMessage,
) -> None:
    try:
        command_type = msg.get("type")
        payload = msg.get("payload", {})

        log.info(
            "Processing command %s from %s",
            command_type,
            message.message_id[:10] if message.message_id else "unknown",
        )

        await dp.dispatch(
            command_type,
            payload,
        )

        log.info(
            "Command %s processed successfully",
            command_type,
        )
    except Exception:
        log.exception("Error processing command")
        raise


class IncomingMessage(BaseModel):
    type: str
    payload: dict[str, Any]


@broker.subscriber("qry.affirmations")
async def handle_queries(
    msg: IncomingMessage,
    message: RabbitMessage,
) -> Any:
    try:
        log.info(
            "Processing query %s from %s",
            msg.type,
            message.message_id[:10] if message.message_id else "unknown",
        )

        result = await dp.dispatch(
            msg.type,
            msg.payload,
        )
        log.info("Query processed successfully")

    except Exception as e:
        log.exception("Error processing query")
        return {
            "status": "error",
            "message": str(e),
        }
    else:
        return result
