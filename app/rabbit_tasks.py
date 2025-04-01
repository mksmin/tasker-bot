import json
import aio_pika
import aiohttp
import asyncio

from config import settings
from database import Task
from database.requests import get_list_of_all_tasks


async def process_task(message: aio_pika.IncomingMessage):
    async with message.process():
        # 1. Извлекаем данные из сообщения
        task_data = json.loads(message.body.decode())
        endpoint = task_data.get("endpoint")
        data = task_data.get("data", {})

        print(f"Получено сообщение от {message.routing_key} с данными: {data}")

        # 3. Выполняем логику (пример)
        user_id = data.get("user_tg_id")
        tasks = await get_list_of_all_tasks(user_tg=user_id)
        formatted_tasks = {i: task.text_task for i, task in enumerate(tasks, 1)}

        # 4. Формируем ответ для отправки обратно
        response_data = {
            "status": "success",
            "user_id": user_id,
            "tasks": formatted_tasks,
        }

        print(
            f"Получено сообщение от {message.routing_key} с данными"
        )

        # 1. Получаем канал из сообщения
        channel = message.channel

        # 2. Явно объявляем exchange (default)
        exchange = await channel.get_exchange("")  # Теперь работает в 9.5.5

        # 3. Отправляем ответ
        await exchange.publish(
            aio_pika.Message(
                body=json.dumps(response_data).encode(),
                correlation_id=message.correlation_id,
            ),
            routing_key=message.reply_to,
        )