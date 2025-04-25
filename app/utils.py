from aiogram import Bot

from app import keyboards as kb
from config import logger
from database import requests as rq, Task


async def send_daily_tasks(user_tgid: int, bot: Bot) -> None:
    settings = await rq.get_user_settings(user_tg=user_tgid)

    tasks: list[Task] = await rq.get_list_of_random_tasks(user_tg=user_tgid, count=settings.count_tasks)
    list_of_tasks = [task.text_task for task in tasks]

    if len(list_of_tasks) <= 0:
        logger.info(f'No daily tasks to send to user {user_tgid}')
        return

    stroke_tasks = '\n'.join(f'{i}. {task}' for i, task in enumerate(list_of_tasks, 1))
    msg_to_send = (f'Доброе утро, вот твои аффирмации на сегодня:\n\n'
                   f'{stroke_tasks}')
    try:
        await bot.send_message(chat_id=user_tgid, text=msg_to_send, reply_markup=kb.finishing_task)
        logger.info(f'Daily tasks sent to user {user_tgid}')
    except Exception as e:
        logger.error(f'Error while sending daily tasks to user {user_tgid}: {e}')
        raise e
