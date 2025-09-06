from aiogram import Bot

from bot import keyboards as kb
from config import logger
from database import requests as rq
from database.crud import crud_manager


async def send_daily_tasks(user_tgid: int, bot: Bot) -> None:
    settings = await rq.get_user_settings(user_tg=user_tgid)

    tasks = await crud_manager.task.get_random_tasks(
        user_tg=user_tgid,
        count=settings.count_tasks,
    )
    list_of_tasks = [task.text_task for task in tasks]

    if len(list_of_tasks) <= 0:
        logger.info(f"No daily tasks to send to user %s", user_tgid)
        return

    stroke_tasks = "\n".join(f"{i}. {task}" for i, task in enumerate(list_of_tasks, 1))
    msg_to_send = f"Доброе утро, вот твои аффирмации на сегодня:\n\n{stroke_tasks}"
    try:
        await bot.send_message(
            chat_id=user_tgid,
            text=msg_to_send,
            reply_markup=kb.finishing_task,
        )
        logger.info(f"Daily tasks sent to user %s", user_tgid)
    except Exception as e:
        logger.error(f"Error while sending daily tasks to user %s: $s", user_tgid, e)
        raise e
