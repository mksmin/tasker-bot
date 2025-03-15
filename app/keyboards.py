from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

finishing_task = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Завершить задачу", callback_data="finish_task")]
    ])