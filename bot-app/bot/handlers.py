# import from lib
from datetime import time
from typing import cast

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User
from sqlalchemy import select

# import from modules
from bot import keyboards as kb
from bot import statesuser as st
from config import logger
from database import SettingsRepo, db_helper, user_settings_ctx
from database import requests as rq
from database.crud import crud_manager
from database.models import UserSettings

from . import update_schedule
from .handler_filtres import (
    HasCallbackMessageFilter,
    HasCallbackUserFilter,
    HasUserFilter,
)

# globals
router = Router()


@router.message(
    CommandStart(),
    HasUserFilter(),
)
async def cmd_start(
    message: Message,
    from_user: User,
) -> None:
    user_data = {
        "user_tg": from_user.id,
        "first_name": from_user.first_name,
        "last_name": from_user.last_name,
        "username": from_user.username,
    }

    user = await crud_manager.user.create_user(user_data=user_data)
    await rq.get_user_settings(user_tg=user.user_tg)
    await message.answer(
        "Привет! \n\n"
        "Отправь мне любые афоризмы <i>(по одной шт за раз)</i>, "
        "а я буду каждый день присылать тебе 5 случайных! \n\n"
        "Обычно я отправляю в 9 утра по Москве. Используй команду /settings, "
        "чтобы изменить время отправки",
    )


@router.message(
    Command("daily"),
    HasUserFilter(),
)
async def cmd_daily_tasks(
    message: Message,
    from_user: User,
) -> None:
    user_tgid = from_user.id

    settings = await rq.get_user_settings(user_tg=user_tgid)

    tasks = await crud_manager.task.get_random_tasks(
        user_tg=user_tgid,
        count=settings.count_tasks,
    )

    if len(tasks) <= 0:
        logger.info("No daily tasks to send to user %d", user_tgid)
        await message.answer("У тебя нет сохраненных текстов")
        return

    stroke_tasks = "\n".join(
        f"{i}. {task.text_task}" for i, task in enumerate(tasks, 1)
    )
    msg_to_send = f"Доброе утро, вот твои аффирмации на сегодня:\n\n{stroke_tasks}"

    await message.answer(text=msg_to_send, reply_markup=kb.finishing_task)
    logger.info("Daily tasks sent to user %d", user_tgid)


@router.message(
    Command("settings"),
    HasUserFilter(),
)
async def cmd_settings(
    message: Message,
    state: FSMContext,
    from_user: User,
) -> None:
    await state.clear()
    repo: SettingsRepo = user_settings_ctx.get()
    user = await crud_manager.user.get_user(user_tg=from_user.id)

    n = await repo.get(user.id)

    if not n:
        logger.debug("User has no settings. Creating new one...")
        await repo.set(user_id=user.id)
        n = cast(
            UserSettings,
            await repo.get(user.id),
        )

    await message.answer(
        f"<b>Текущие настройки</b>\n\n"
        f"<b>{n.count_tasks}</b> — столько отправляется тебе аффирмаций в день\n"
        f"<b>{n.send_time.strftime('%H:%M')} (мск)</b> — время отправки\n",
        reply_markup=kb.settings_start,
    )


@router.callback_query(
    F.data == "change_settings",
    HasCallbackMessageFilter(),
)
async def cmd_change_settings(
    callback_message: Message,
) -> None:
    await callback_message.edit_text(
        "Выбери, что хочешь изменить",
        reply_markup=kb.settings_change,
    )


@router.callback_query(
    F.data == "change_amount",
    HasCallbackUserFilter(),
    HasCallbackMessageFilter(),
)
async def cmd_change_amount(
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
    F.data == "change_time",
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
            query = select(UserSettings).where(UserSettings.user_id == user.id)
            executed = await session.execute(query)
            user_setting = executed.scalar_one()
            user_setting.send_time = new_time
            session.add(user_setting)
            await session.commit()

        await update_schedule(
            user_tg_id=from_user.id,
            new_time=new_time,
            bot=cast(
                Bot,
                message.bot,
            ),
        )

        await message.answer(
            f"Установил время отправки аффирмаций: {new_time} (мск). "
            f"Проверь настройки командой /settings",
        )
        await state.set_state(st.Settings.time_minute)

    except Exception as e:
        logger.error("Ошибка при изменении настроек: %s", e, exc_info=True)
        await message.answer(f"Ошибка при изменении настроек, {e}")
        await state.clear()
        return


@router.callback_query(
    F.data == "back_to_settings",
    HasCallbackMessageFilter(),
)
async def cmd_back_to_settings(
    callback_message: Message,
) -> None:
    await callback_message.edit_text(
        "Ничего менять не будем. Вызови команду /settings, "
        "чтобы вернуться к настройкам",
    )


@router.message(
    F.text,
    HasUserFilter(),
)
async def user_add_task(
    message: Message,
    state: FSMContext,
    from_user: User,
) -> None:
    await state.clear()

    user_data = {
        "first_name": from_user.first_name,
        "last_name": from_user.last_name,
        "username": from_user.username,
    }
    # TODO: сделать метод для crud_manager на обновление данных пользователя
    # TODO: и заменить метод get_user_by_tgid на него
    await rq.get_user_by_tgid(from_user.id, user_data=user_data)
    await rq.get_user_settings(user_tg=from_user.id)

    if not message.text:
        await message.answer("Возникла ошибка при добавлении аффирмации")
        return

    try:
        task_added = await crud_manager.task.create_task(
            task_text=message.text,
            user_tg=from_user.id,
        )
    except Exception:
        await message.answer(
            "Возникла ошибка при добавлении аффирмации. Операция отменена",
        )
        return

    if task_added:
        await message.answer(
            f"Добавил аффирмацию: \n\n{task_added.text_task}",
            reply_markup=kb.list_of_tasks,
        )
    else:
        await message.answer("Возникла ошибка")
