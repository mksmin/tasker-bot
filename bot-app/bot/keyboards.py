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
back_to_settings = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Вернуться к настройкам",
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


class CountTasksCallback(
    CallbackData,
    prefix="set",
):
    action: str
    value: int


def set_count_tasks_kb(
    num: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i in range(1, num + 1):
        builder.button(
            text=str(i),
            callback_data=CountTasksCallback(
                action="choose_count",
                value=i,
            ).pack(),
        )
    builder.row(
        InlineKeyboardButton(
            text="Отмена",
            callback_data="set:cancel_change_settings",
        ),
    )
    builder.adjust(5)
    return builder.as_markup()


class TimePickerCallback(CallbackData, prefix="time"):
    action: str
    hour: int | None = None
    minute: int | None = None


def hour_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for h in range(24):
        builder.button(
            text=f"{h:02d}",
            callback_data=TimePickerCallback(
                action="hour",
                hour=h,
            ).pack(),
        )
    builder.row(
        InlineKeyboardButton(
            text="Отмена",
            callback_data="set:cancel_change_settings",
        ),
    )
    builder.adjust(6)
    return builder.as_markup()


def minute_keyboard(
    hour: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for m in [0, 15, 30, 45]:
        builder.button(
            text=f"{m:02d}",
            callback_data=TimePickerCallback(
                action="minute",
                hour=hour,
                minute=m,
            ).pack(),
        )
    builder.row(
        InlineKeyboardButton(
            text="Задать минуты вручную",
            callback_data="set:custom_time",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Отмена",
            callback_data="set:cancel_change_settings",
        ),
    )
    builder.adjust(4)
    return builder.as_markup()
