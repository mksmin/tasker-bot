from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

finishing_task = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Удалить аффирмацию", callback_data="finish_task")]
    ])

list_of_tasks = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Все аффирмации", callback_data="my_tasks")],
])