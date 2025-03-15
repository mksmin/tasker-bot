# import from lib
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

# import from modules
from database import Task
from database import requests as rq

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.get_user_by_tgid(message.from_user.id)
    await message.answer("Привет! Добавляй задачи, а я буду каждый день присылать 5 случайных! ")


@router.message(F.text)
async def user_add_task(message: Message):
    task_added = await rq.add_task(
        user_tg=message.from_user.id,
        user_text=message.text
    )

    if task_added:
        await message.answer(f"Добавил таску {message.text}")
    else:
        await message.answer(f"Возникла ошибка")


async def send_daily_tasks(user_tgid: int, bot: Bot) -> None:
    tasks: list[Task] = await rq.get_list_of_random_tasks(used_tg=user_tgid)

    if not tasks:
        await bot.send_message(
            chat_id=user_tgid,
            text="У вас нету тасок на сегодня")
        return

    list_of_tasks = [task.text_task for task in tasks]
    stroke_tasks = '\n'.join(f'{i}. {task}' for i, task in enumerate(list_of_tasks, 1))
    msg_to_send = (f'Доброе утро, вот твои таски на сегодня:\n\n'
                   f'{stroke_tasks}')

    await bot.send_message(chat_id=user_tgid, text=msg_to_send)