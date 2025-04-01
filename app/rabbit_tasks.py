import json
import aio_pika
import aiohttp
import asyncio

from config import settings
from database import Task
from database.requests import get_list_of_all_tasks


async def process_task(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            # 1. Извлекаем данные из сообщения
            task_data = json.loads(message.body.decode())
            endpoint = task_data.get("endpoint")
            data = task_data.get("data", {})

            print(f"Получено сообщение от {message.routing_key} с данными: {data}")

            # 2. Выполняем основную логику
            user_id = data.get("user_tg_id")
            tasks = await get_list_of_all_tasks(user_tg=user_id)  # Ваша функция получения задач
            formatted_tasks = {i: task.text_task for i, task in enumerate(tasks, 1)}

            # 3. Формируем ответ
            response_data = {
                "status": "success",
                "user_id": user_id,
                "tasks": formatted_tasks,
            }

            # --- АЛЬТЕРНАТИВНЫЙ КОД ОТПРАВКИ ОТВЕТА ---
            # Создаем новое подключение для отправки ответа
            async with aio_pika.connect_robust(settings.rabbit.url) as connection:
                channel = await connection.channel()

                # Отправляем ответ через default exchange
                await channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(response_data).encode(),
                        correlation_id=message.correlation_id,  # Сохраняем correlation_id
                    ),
                    routing_key=message.reply_to,  # Используем очередь из reply_to
                )

        except Exception as e:
            print(f"Ошибка обработки задачи: {e}")
            raise