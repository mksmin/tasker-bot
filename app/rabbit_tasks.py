# import libs
import aio_pika
import json

# import from libs
from functools import wraps
from typing import Callable
from faststream.rabbit import RabbitBroker, RabbitMessage

# import from project
from config import settings, logger
from database.crud import crud_manager

# globals
broker = RabbitBroker(settings.rabbit.url)


class RabbitCommandRouter:
    def __init__(self):
        self._routes: dict[str, Callable] = {}

    def register(self, command_name: str):
        def decorator(func: Callable):
            self._routes[command_name] = func
            return func

        return decorator

    def get_handler(self, command_name: str) -> Callable:
        handler = self._routes.get(command_name)
        if not handler:
            raise ValueError(
                f"Не известная команда: {command_name}. Доступные команды: {list(self._routes.keys())}"
            )

        return handler

    async def handle(self, command_name: str, data: dict):
        handler = self.get_handler(command_name)
        return await handler(data)


router = RabbitCommandRouter()


@router.register("create_task")
async def create_task(data: dict):
    return await crud_manager.task.create_task(**data)


@router.register("get_task")
async def get_task(data: dict):
    return await crud_manager.task.get_task_by_id(**data)


@router.register("get_random_tasks")
async def get_random_tasks(data: dict):
    return await crud_manager.task.get_random_tasks(**data)


@router.register("get_paginated_tasks")
async def get_paginated_tasks(data: dict):
    return await crud_manager.task.get_paginated_tasks(**data)


@router.register("mark_as_done")
async def mark_as_done(data: dict):
    return await crud_manager.task.mark_as_done(**data)


@broker.subscriber("affirmations")
async def process_task(msg: dict | bytes, message: RabbitMessage):
    try:
        if isinstance(msg, bytes):
            msg = json.loads(msg.decode())

        command = msg.get("command")
        data = msg.get("payload", {})

        logger.info("Получено сообщение от %s с командой %s.", message.message_id[:11], command)

        result = await router.handle(command, data)
        return result

    except Exception as e:
        logger.error("Ошибка обработки задачи: %s", e)
        raise
