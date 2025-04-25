import json
import aio_pika
import aiohttp
import asyncio

from config import settings
from database import Task
from database.requests import get_list_of_all_tasks, get_user_relationship


async def process_task(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            # 1. Извлекаем данные из сообщения
            task_data = json.loads(message.body.decode())
            endpoint = task_data.get("endpoint")
            data = task_data.get("data", {})

            print(f"Получено сообщение от {message.routing_key} с данными: {data}")
            user_data = {}
            for key, value in data.items():
                if key == "user_tg_id":
                    continue

                user_data[key] = value

            # 2. Выполняем основную логику
            user_id = int(data.get("user_tg_id"))
            tasks = await get_list_of_all_tasks(user_tg=user_id, user_data=user_data)
            user = await get_user_relationship(user_tg=user_id)
            formatted_tasks = [
                {"id": task.id, "number": idx, "text": task.text_task}
                for idx, task in enumerate(tasks, 1)
            ]

            # 3. Формируем ответ
            response_data = {
                "status": "success",
                "user_id": user_id,
                "tasks": formatted_tasks,
                "settings": {
                    "send_time": str(user.settings.send_time),
                    "count_tasks": user.settings.count_tasks
                }
            }

            # --- ИСПРАВЛЕННЫЙ БЛОК ОТПРАВКИ ---
            # Создаем новое подключение
            connection = await aio_pika.connect_robust(settings.rabbit.url)
            channel = await connection.channel()

            try:
                # Отправляем ответ через default exchange
                await channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(response_data).encode(),
                        correlation_id=message.correlation_id,
                    ),
                    routing_key=message.reply_to,
                )
            finally:
                # Закрываем соединение вручную
                await connection.close()

        except Exception as e:
            print(f"Ошибка обработки задачи: {e}")
            raise