from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

finishing_task = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Удалить аффирмацию", callback_data="finish_task")]
    ]
)

list_of_tasks = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Все аффирмации",
                web_app=WebAppInfo(url="https://api.mks-min.ru/apps/bot2"),
            )
        ],
    ]
)

settings_start = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Изменить настройки", callback_data="change_settings"
            )
        ]
    ]
)

settings_change = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Количество аффирмаций", callback_data="change_amount"
            ),
            InlineKeyboardButton(text="Время отправки", callback_data="change_time"),
        ],
        [
            InlineKeyboardButton(
                text="Вернуться назад", callback_data="back_to_settings"
            )
        ],
    ]
)
