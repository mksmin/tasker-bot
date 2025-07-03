from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.crud import crud_manager


router = Router()


@router.message(Command("test_reg"))
async def test_reg(message: Message):
    user_data = {
        "user_tg": 123456,
        "first_name": "John Test",
    }

    instance = await crud_manager.user.create(user_data)
    if instance:
        print("User created successfully!")
        await message.answer(f"Hello, {instance.first_name}!  id={instance.id}, created_at={instance.created_at}")