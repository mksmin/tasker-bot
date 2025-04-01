import json
import aio_pika
import aiohttp
import asyncio

from config import settings
from database import Task
from database.requests import get_list_of_all_tasks


async def process_task(message: aio_pika.IncomingMessage):
    async with message.process():
        task_data = json.loads(message.body.decode())
        request = task_data.get('request', None)
        endpoint = task_data.get('endpoint', None)
        data = task_data.get('data', None)

        # print(f'Request: {request}'
        #       f'\nEndpoint: {endpoint}'
        #       f'\nData: {data}')
        #
        # print(f"type: {type(data)}")
        # print(f"tg_id: {data.get('user_tg_id', None)}")

        if request == "GET" and endpoint == "/user/affirmations":
            user_id = data.get('user_tg_id', None)
            result: list[Task] = await get_list_of_all_tasks(user_tg=user_id)
            data_response = {
                "user_id": user_id,
                "details": {

                }
            }
            for i, task in enumerate(result, start=1):
                if task.text_task:
                    data_response["details"][i] = task.text_task
                else:
                    data_response["details"][i] = ""

            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.mks-min.ru/tasks', json=data_response) as response:
                    json_response = await response.json()
                    status_code = response.status

