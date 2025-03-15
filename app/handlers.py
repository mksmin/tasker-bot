# import from lib
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

# import from modules
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
