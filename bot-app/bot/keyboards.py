from enum import StrEnum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

list_of_tasks = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Все аффирмации",
                web_app=WebAppInfo(url="https://api.mks-min.ru/apps/bot2"),
            ),
        ],
    ],
)

settings_start = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Изменить настройки",
                callback_data="change_settings",
            ),
        ],
    ],
)


class SettingsAction(StrEnum):
    change_amount = "change_amount"
    change_time = "change_time"
    switch_sending = "switch_sending"
    cancel = "cancel_change_settings"


class SettingsCB(
    CallbackData,
    prefix="set",
):
    action: SettingsAction


def settings_kb(*, sending_on: bool) -> InlineKeyboardMarkup:
    mark = "✅" if sending_on else "❌"
    turn_text = "включена" if sending_on else "выключена"
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Количество аффирмаций",
        callback_data=SettingsCB(action=SettingsAction.change_amount),
    )
    builder.button(
        text="Время отправки",
        callback_data=SettingsCB(action=SettingsAction.change_time),
    )
    builder.button(
        text=f"{mark} Отправка {turn_text}",
        callback_data=SettingsCB(action=SettingsAction.switch_sending),
    )
    builder.button(
        text="Отмена",
        callback_data=SettingsCB(action=SettingsAction.cancel),
    )
    builder.adjust(2, 1, 1)
    return builder.as_markup()
