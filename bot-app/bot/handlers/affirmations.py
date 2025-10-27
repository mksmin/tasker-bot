import logging

from aiogram import (
    F,
    Router,
    html,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User

from bot import keyboards as kb
from bot.handler_filtres import HasUserFilter
from database import requests as rq
from database.crud import crud_manager

router = Router()
log = logging.getLogger(__name__)


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
        log.info("No daily tasks to send to user %d", user_tgid)
        await message.answer("У тебя нет сохраненных аффирмаций")
        return

    stroke_tasks = "\n".join(
        f"{i}. {html.code(task.text_task)} \n" for i, task in enumerate(tasks, 1)
    )
    msg_to_send = f"Привет! Вот твои аффирмации на сегодня:\n\n{stroke_tasks}"

    await message.answer(text=msg_to_send)
    log.info("Daily tasks sent to user %d", user_tgid)


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
