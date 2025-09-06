import json
from collections.abc import Awaitable
from functools import wraps
from typing import Any, Callable, cast

import aio_pika
from faststream.rabbit import RabbitBroker, RabbitMessage
from pydantic import BaseModel

# import from project
from config import logger, settings
from database.crud import crud_manager
from database.schemas import TaskReadSchema

# globals
broker = RabbitBroker(settings.rabbit.url)
Handler = Callable[[dict[str, Any]], Awaitable[Any]]


class RabbitCommandRouter:
    def __init__(self) -> None:
        self._routes: dict[str, Handler] = {}

    def register(
        self,
        command_name: str,
    ) -> Callable[[Handler], Handler]:
        def decorator(func: Handler) -> Handler:
            self._routes[command_name] = func
            return func

        return decorator

    def get_handler(
        self,
        command_name: str,
    ) -> Handler:
        handler = self._routes.get(command_name)
        if not handler:
            msg_error = (
                f"Неизвестная команда: {command_name}. "
                f"Доступные команды: {list(self._routes.keys())}"
            )
            raise ValueError(msg_error)

        return handler

    async def handle(
        self,
        command_name: str,
        data: dict[str, Any],
    ) -> Any:
        handler = self.get_handler(command_name)
        return await handler(data)


router = RabbitCommandRouter()


class CreateTaskRequest(BaseModel):
    user_tg: int
    task_text: str


@router.register("create_task")
async def create_task(data: dict[str, int | str]) -> TaskReadSchema:
    task_data = CreateTaskRequest(**data)
    return await crud_manager.task.create_task(**task_data.model_dump())


@router.register("get_task")
async def get_task(data: dict[str, int]) -> TaskReadSchema:
    return await crud_manager.task.get_task_by_id(**data)


@router.register("get_random_tasks")
async def get_random_tasks(data: dict[str, int]) -> list[TaskReadSchema]:
    return await crud_manager.task.get_random_tasks(**data)


@router.register("get_paginated_tasks")
async def get_paginated_tasks(data: dict[str, int]) -> list[TaskReadSchema]:
    return await crud_manager.task.get_paginated_tasks(**data)


@router.register("mark_as_done")
async def mark_as_done(data: dict[str, int]) -> bool:
    return await crud_manager.task.mark_as_done(**data)


@broker.subscriber("affirmations")
async def process_task(
    msg: dict[str, Any] | bytes,
    message: RabbitMessage,
) -> Any:
    try:
        if isinstance(msg, bytes):
            msg_dict: dict[str, Any] = json.loads(msg.decode())
        else:
            msg_dict = msg

        command = cast(str, msg_dict.get("command"))
        data = msg_dict.get("payload", {})

        logger.info(
            "Получено сообщение от %s с командой %s.",
            message.message_id[:11],
            command,
        )

        return await router.handle(command, data)

    except Exception as e:
        logger.error("Ошибка обработки задачи: %s", e)
        raise
