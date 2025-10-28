import logging

from aiogram import (
    F,
    Router,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User

from app_exceptions.exceptions import UserHasNoTasksError
from bot import keyboards as kb
from bot.dependencies import get_list_user_tasks, prepare_user_message_for_tasks
from bot.handler_filtres import HasUserFilter
from database import requests as rq
from database.crud import crud_manager
from schemas.users import UserSettingsWithUserResponseSchema

router = Router()
log = logging.getLogger(__name__)


@router.message(
    Command("daily"),
    HasUserFilter(),
    flags={
        "user_settings": True,
    },
)
async def cmd_daily_tasks(
    message: Message,
    user_settings_db: UserSettingsWithUserResponseSchema,
) -> None:
    try:
        tasks = await get_list_user_tasks(user_settings_db.user.user_tg)
        msg_to_send = prepare_user_message_for_tasks(tasks)
        await message.answer(text=msg_to_send)
        log.info("Daily tasks sent to user %d", user_settings_db.user.user_tg)
    except UserHasNoTasksError:
        log.info("No daily tasks to send to user %d", user_settings_db.user.user_tg)
        await message.answer("У тебя нет сохраненных аффирмаций")


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
