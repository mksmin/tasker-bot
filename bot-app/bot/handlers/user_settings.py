import logging
from datetime import time
from typing import cast

from aiogram import F
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import User

from bot import keyboards as kb
from bot import statesuser as st
from bot.handler_filtres import HasCallbackMessageFilter
from bot.handler_filtres import HasCallbackUserFilter
from bot.handler_filtres import HasUserFilter
from bot.keyboards import CountTasksCallback
from bot.keyboards import TimePickerCallback
from bot.scheduler import scheduler_instance
from crud.crud_service import CRUDService
from schemas.users import UserSettingsWithUserResponseSchema

router = Router()
log = logging.getLogger(__name__)

MINIMUM_MINUTE = 0
MAXIMUM_MINUTE = 59


@router.message(
    Command("settings"),
    HasUserFilter(),
    flags={
        "user_settings": True,
    },
)
async def cmd_settings(
    message: Message,
    state: FSMContext,
    user_settings_db: UserSettingsWithUserResponseSchema,
) -> None:
    await state.clear()

    send_enable = (
        "✅ Отправка включена"
        if user_settings_db.send_enable
        else "❌ Отправка выключена"
    )
    await message.answer(
        f"⚙️ <b>Настройки</b>\n\n"
        f"<b>{send_enable}</b>\n"
        f"<b>{user_settings_db.count_tasks}</b> "
        f"— столько отправляется тебе аффирмаций в день\n"
        f"<b>{user_settings_db.send_time.strftime('%H:%M')} (мск)</b> "
        f"— время отправки\n",
        reply_markup=kb.settings_start,
    )


@router.callback_query(
    F.data == "change_settings",
    HasCallbackMessageFilter(),
    HasUserFilter(),
    flags={
        "user_settings": True,
    },
)
async def cmd_change_settings(
    _callback: CallbackQuery,
    callback_message: Message,
    user_settings_db: UserSettingsWithUserResponseSchema,
) -> None:
    await callback_message.edit_text(
        "Выбери, что хочешь изменить",
        reply_markup=kb.settings_kb(
            sending_on=user_settings_db.send_enable,
        ),
    )
    await _callback.answer()


@router.callback_query(
    F.data == "set:switch_sending",
    HasCallbackUserFilter(),
    HasCallbackMessageFilter(),
)
async def cmd_switch_sending(
    _callback: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
    from_user: User,
    crud_service: CRUDService,
) -> None:
    user_settings = await crud_service.user.get_user_settings(from_user.id)
    user_settings.send_enable = not user_settings.send_enable
    updated_settings = await crud_service.user.update_user_settings(
        user_tg=from_user.id,
        settings_in=user_settings,
    )
    if updated_settings.send_enable:
        scheduler_instance.add_or_update_job(
            user_settings=updated_settings,
        )
    else:
        scheduler_instance.remove_job(
            user_id=updated_settings.user.id,
        )
    try:
        await callback_message.edit_text(
            "Выбери, что хочешь изменить",
            reply_markup=kb.settings_kb(
                sending_on=user_settings.send_enable,
            ),
        )
    except TelegramBadRequest as e:
        error_message = (
            f"Ошибка во время обновления настроек пользователя {from_user.id}: {e}"
        )
        log.exception(error_message)
        message = "Кажется, настройки уже были изменены"
        await _callback.answer(message)
    else:
        message = (
            "Отправка включена"
            if updated_settings.send_enable
            else "Отправка выключена"
        )
        await _callback.answer(message)
    finally:
        await state.clear()


@router.callback_query(
    F.data == "set:change_amount",
    HasCallbackMessageFilter(),
    flags={
        "user_settings": True,
    },
)
async def cmd_change_amount(
    _callback: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
    user_settings_db: UserSettingsWithUserResponseSchema,
) -> None:
    await state.set_state(st.Settings.count_tasks)
    await callback_message.edit_text(
        f"Выбери, сколько тебе отправлять аффирмаций в день. "
        f"Сейчас я отправляю в день аффирмаций: <b>{user_settings_db.count_tasks}</b>",
        reply_markup=kb.set_count_tasks_kb(5),
    )
    await _callback.answer()


@router.callback_query(
    st.Settings.count_tasks,
    CountTasksCallback.filter(F.action == "choose_count"),
    HasCallbackUserFilter(),
    HasCallbackMessageFilter(),
)
async def set_count_of_affirm2(
    _callback: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
    from_user: User,
    callback_data: CountTasksCallback,
    crud_service: CRUDService,
) -> None:
    user_settings = await crud_service.user.get_user_settings(from_user.id)
    user_settings.count_tasks = callback_data.value
    updated_settings = await crud_service.user.update_user_settings(
        user_tg=from_user.id,
        settings_in=user_settings,
    )

    await callback_message.edit_text(
        f"Установил число случайных аффирмаций в день: {updated_settings.count_tasks}",
        reply_markup=kb.back_to_settings,
    )
    await _callback.answer()
    await state.clear()


@router.callback_query(
    F.data == "set:change_time",
    HasCallbackMessageFilter(),
    flags={
        "user_settings": True,
    },
)
async def cmd_change_time(
    _callback: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
    user_settings_db: UserSettingsWithUserResponseSchema,
) -> None:
    await callback_message.edit_text(
        f"🕐"
        f"Выбери час отправки аффирмаций (мск).\n"
        f"Текущее время отправки: <b>{user_settings_db.send_time:%H:%M}</b>",
        reply_markup=kb.hour_keyboard(),
    )
    await _callback.answer()
    await state.set_state(st.Settings.time_hour)


@router.callback_query(
    st.Settings.time_hour,
    TimePickerCallback.filter(F.action == "hour"),
    HasCallbackMessageFilter(),
)
async def choose_minutes(
    _callback: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
    callback_data: TimePickerCallback,
) -> None:
    callback_data.hour = cast(
        int,
        callback_data.hour,
    )
    await state.update_data(time_hour=callback_data.hour)
    await callback_message.edit_text(
        f"Выбран час: <b>{callback_data.hour:02d}</b>\nТеперь выбери минуты:",
        reply_markup=kb.minute_keyboard(callback_data.hour),
    )
    await _callback.answer()
    await state.set_state(st.Settings.time_minute)


@router.callback_query(
    st.Settings.time_minute,
    F.data == "set:custom_time",
    HasCallbackMessageFilter(),
)
async def cmd_custom_minutes(
    _callback: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
) -> None:
    data = await state.get_data()
    await callback_message.edit_text(
        f"Выбран час: <b>{data.get('time_hour', 0):02d}</b>\n"
        f"Теперь введи минуты вручную (0–59):",
    )
    await _callback.answer()
    await state.set_state(st.Settings.time_custom_minute)


@router.callback_query(
    st.Settings.time_minute,
    TimePickerCallback.filter(F.action == "minute"),
    HasCallbackUserFilter(),
    HasCallbackMessageFilter(),
)
async def confirm_time(
    _callback: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
    callback_data: TimePickerCallback,
    crud_service: CRUDService,
    from_user: User,
) -> None:
    hour = cast(int, callback_data.hour)
    minute = cast(int, callback_data.minute)
    new_time = time(hour=hour, minute=minute)

    user_settings = await crud_service.user.get_user_settings(from_user.id)
    user_settings.send_time = new_time
    updated_settings = await crud_service.user.update_user_settings(
        user_tg=from_user.id,
        settings_in=user_settings,
    )
    scheduler_instance.add_or_update_job(
        user_settings=updated_settings,
    )
    await callback_message.edit_text(
        f"✅ Время отправки аффирмаций установлено: "
        f"<b>{updated_settings.send_time:%H:%M}</b> (мск).\n"
        f"Проверь настройки командой /settings",
    )
    await _callback.answer()
    await state.clear()


@router.message(
    st.Settings.time_custom_minute,
    F.text.regexp(r"^\d+$"),
    HasUserFilter(),
)
async def cmd_save_custom_minutes(
    message: Message,
    state: FSMContext,
    crud_service: CRUDService,
    from_user: User,
) -> None:
    minute = int(
        cast(
            str,
            message.text,
        ),
    )

    if not MINIMUM_MINUTE <= minute <= MAXIMUM_MINUTE:
        await message.answer("Ошибка: нужно число от 0 до 59. Попробуй снова.")
        return

    data = await state.get_data()
    hour = int(data["time_hour"])
    new_time = time(hour=hour, minute=minute)

    user_settings = await crud_service.user.get_user_settings(from_user.id)
    user_settings.send_time = new_time
    updated_settings = await crud_service.user.update_user_settings(
        user_tg=from_user.id,
        settings_in=user_settings,
    )

    scheduler_instance.add_or_update_job(
        user_settings=updated_settings,
    )

    await message.answer(
        f"✅ Время отправки аффирмаций установлено: "
        f"<b>{updated_settings.send_time:%H:%M}</b> (мск).\n"
        f"Проверь настройки командой /settings",
    )
    await state.clear()


@router.callback_query(
    F.data == "set:cancel_change_settings",
    HasCallbackMessageFilter(),
)
async def cmd_back_to_settings(
    _callback: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
) -> None:
    await callback_message.edit_text(
        "Ничего менять не будем. Вызови команду /settings, "
        "чтобы вернуться к настройкам",
    )
    await _callback.answer()
    await state.clear()
