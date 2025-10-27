import logging
from datetime import time
from typing import cast

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from bot import keyboards as kb
from bot import statesuser as st
from bot.handler_filtres import (
    HasCallbackMessageFilter,
    HasCallbackUserFilter,
    HasUserFilter,
)
from bot.scheduler import scheduler_instance
from crud.crud_service import CRUDService
from database import UserSettings, db_helper
from database.crud import crud_manager
from schemas.users import (
    UserSettingsWithUserReadSchema,
    UserSettingsWithUserResponseSchema,
)

router = Router()
log = logging.getLogger(__name__)


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

    await callback_message.edit_text(
        "Выбери, что хочешь изменить",
        reply_markup=kb.settings_kb(
            sending_on=user_settings.send_enable,
        ),
    )
    message = (
        "Отправка включена" if updated_settings.send_enable else "Отправка выключена"
    )
    await _callback.answer(message)
    await state.clear()


@router.callback_query(
    F.data == "set:change_amount",
    HasCallbackUserFilter(),
    HasCallbackMessageFilter(),
)
async def cmd_change_amount(
    _callback: CallbackQuery,
    state: FSMContext,
    from_user: User,
    callback_message: Message,
) -> None:
    await state.set_state(st.Settings.count_tasks)
    user = await crud_manager.user.get_user(user_tg=from_user.id)
    async for session in db_helper.session_getter():
        query = select(UserSettings).where(UserSettings.user_id == user.id)
        executed = await session.execute(query)
        settings = executed.scalar_one()

        await callback_message.edit_text(
            f"Отправь число, которое должно быть меньше или равно 5 и больше 0"
            f"\nСейчас у тебя {settings.count_tasks} аффирмаций",
        )


@router.message(
    st.Settings.count_tasks,
    F.text.regexp(r"^\d+$"),
    HasUserFilter(),
)
async def set_count_of_affirm(
    message: Message,
    state: FSMContext,
    from_user: User,
) -> None:
    min_len_text = 1
    max_len_text = 5
    if (
        int(cast(str, message.text)) > max_len_text
        or int(cast(str, message.text)) < min_len_text
    ):
        await message.answer(
            "Ты ошибся, число должно быть меньше или равно 5 и больше 0",
        )
    else:
        user = await crud_manager.user.get_user(user_tg=from_user.id)

        await state.update_data(count_tasks=message.text)
        data = await state.get_data()
        try:
            async for session in db_helper.session_getter():
                query = select(UserSettings).where(UserSettings.user_id == user.id)
                executed = await session.execute(query)
                user_setting = executed.scalar_one()
                user_setting.count_tasks = int(data["count_tasks"])
                session.add(user_setting)
                await session.commit()

            await message.answer(f"Установил число аффирмаций: {data['count_tasks']}")
            await state.clear()

        except Exception as e:
            await message.answer(f"Ошибка при изменении настроек, {e}")
            await state.clear()
            return


@router.callback_query(
    F.data == "set:change_time",
    HasCallbackMessageFilter(),
)
async def cmd_change_time(
    callback: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
) -> None:
    await state.set_state(st.Settings.time_hour)
    user = await crud_manager.user.get_user(user_tg=callback.from_user.id)

    async for session in db_helper.session_getter():
        query = select(UserSettings).where(UserSettings.user_id == user.id)
        executed = await session.execute(query)
        settings = executed.scalar_one()

        await callback_message.edit_text(
            "Отправь число от 0 до 23, это будет час отправки аффирмаций",
            f"\nСейчас время отправки {settings.send_time} ",
        )


@router.message(st.Settings.time_hour, F.text.regexp(r"^\d+$"))
async def cmd_set_hour(message: Message, state: FSMContext) -> None:
    min_len_text = 0
    max_len_text = 23
    if (
        int(cast(str, message.text)) > max_len_text
        or int(cast(str, message.text)) < min_len_text
    ):
        await message.answer("Ошибка, число должно быть меньше или равно 23 и больше 0")
    else:
        await state.update_data(time_hour=message.text)
        data = await state.get_data()
        try:
            await message.answer(
                f"Установил час отправки аффирмаций: {data['time_hour']}, "
                f"теперь отправь минуты",
            )
            await state.set_state(st.Settings.time_minute)

        except Exception as e:
            await message.answer(f"Ошибка при изменении настроек, {e}")
            await state.clear()
            return


@router.message(
    st.Settings.time_minute,
    F.text.regexp(r"^\d+$"),
    HasUserFilter(),
)
async def cmd_set_minutes(
    message: Message,
    state: FSMContext,
    from_user: User,
) -> None:
    min_len_text = 0
    max_len_text = 59
    if (
        int(cast(str, message.text)) > max_len_text
        or int(cast(str, message.text)) < min_len_text
    ):
        await message.answer("Ошибка, число должно быть меньше или равно 59 и больше 0")
        return

    await state.update_data(time_minute=message.text)
    data = await state.get_data()
    new_time = time(hour=int(data["time_hour"]), minute=int(data["time_minute"]))

    user = await crud_manager.user.get_user(user_tg=from_user.id)

    try:
        async for session in db_helper.session_getter():
            query = (
                select(UserSettings)
                .where(UserSettings.user_id == user.id)
                .options(
                    joinedload(UserSettings.user),
                )
            )
            executed = await session.execute(query)
            user_setting = executed.scalar_one()
            user_setting.send_time = new_time
            session.add(user_setting)
            await session.commit()

            if user_setting.send_enable:
                scheduler_instance.add_or_update_job(
                    user_settings=UserSettingsWithUserReadSchema.model_validate(
                        user_setting,
                    ),
                )

        await message.answer(
            f"Установил время отправки аффирмаций: {new_time} (мск). "
            f"Проверь настройки командой /settings",
        )
        await state.set_state(st.Settings.time_minute)

    except Exception as e:
        log.exception("Ошибка при изменении настроек")
        await message.answer(f"Ошибка при изменении настроек, {e}")
        await state.clear()
        return


@router.callback_query(
    F.data == "set:cancel_change_settings",
    HasCallbackMessageFilter(),
)
async def cmd_back_to_settings(
    _callback: CallbackQuery,
    callback_message: Message,
) -> None:
    await callback_message.edit_text(
        "Ничего менять не будем. Вызови команду /settings, "
        "чтобы вернуться к настройкам",
    )
