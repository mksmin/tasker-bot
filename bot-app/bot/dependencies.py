import logging

from aiogram import Bot, html
from aiogram.exceptions import TelegramForbiddenError

from app_exceptions.exceptions import UserHasNoTasksError
from crud.crud_service import get_crud_service_with_session

log = logging.getLogger(__name__)


async def get_list_user_tasks(
    user_tg: int,
) -> list[str]:
    async with get_crud_service_with_session() as crud_service:  # type: CRUDService
        tasks = await crud_service.affirm.get_random_affirmations(user_tg=user_tg)

        list_of_tasks = [task.text for task in tasks]
        if len(list_of_tasks) <= 0:
            error_message = f"User {user_tg} has no tasks"
            raise UserHasNoTasksError(error_message)
        return list_of_tasks


def prepare_user_message_for_tasks(
    list_of_tasks: list[str],
) -> str:
    stroke_tasks = "\n".join(
        f"{i}. {html.code(task)} \n" for i, task in enumerate(list_of_tasks, 1)
    )
    return f"Привет! Вот твои аффирмации на сегодня:\n\n{stroke_tasks}"


async def send_daily_tasks(
    bot: Bot,
    user_tg: int,
) -> None:
    try:
        tasks = await get_list_user_tasks(
            user_tg=user_tg,
        )
        msg_to_send = prepare_user_message_for_tasks(tasks)
        await bot.send_message(
            chat_id=user_tg,
            text=msg_to_send,
        )
        log.info("Daily tasks sent to user %s", user_tg)
    except UserHasNoTasksError:
        log.info("No daily tasks to send to user %s", user_tg)
        return
    except TelegramForbiddenError as tfe:
        log.warning(
            "Не удалось отправить сообщение пользователю %s. Message: %s",
            user_tg,
            tfe.message,
        )
