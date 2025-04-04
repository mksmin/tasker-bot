from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

finishing_task = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Удалить аффирмацию", callback_data="finish_task")]
    ])

list_of_tasks = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Все аффирмации", web_app=WebAppInfo(url="https://api.mks-min.ru/affirm"))],
])