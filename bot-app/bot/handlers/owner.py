from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import keyboards as kb
from bot import statesuser as st
from bot.handler_filtres.user_filter import RootPermissionFilter
from bot.scheduler import scheduler_instance
from crud.crud_service import CRUDService

router = Router()


@router.message(
    Command("send"),
    RootPermissionFilter(),
)
async def send_message_to_users(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()
    await state.set_state(st.SendingMessage.value)
    await message.answer("Введите сообщение для отправки")


@router.message(
    st.SendingMessage.value,
    RootPermissionFilter(),
)
async def confirm_message_for_send(
    message: Message,
    state: FSMContext,
) -> None:
    assert message.bot
    await state.update_data(
        value=message.html_text,
    )
    if message.photo:
        await state.update_data(
            image_id=message.photo[-1].file_id,
        )

    data = await state.get_data()

    await message.answer("Вот так будет выглядеть сообщение:")
    if photo_id := data.get("image_id"):
        await message.bot.send_photo(
            chat_id=message.chat.id,
            photo=photo_id,
            caption=data["value"],
        )
    else:
        await message.answer(
            text=data["value"],
        )
    await message.answer(
        "Отправить?",
        reply_markup=kb.sending_message_to_users_kb,
    )


@router.callback_query(
    F.data == "send_message",
    RootPermissionFilter(),
)
async def send_message(
    _callback: CallbackQuery,
    state: FSMContext,
    crud_service: CRUDService,
) -> None:
    if not isinstance(_callback.message, Message):
        return
    if not isinstance(_callback.bot, Bot):
        return

    bot = _callback.bot
    errors_msg = []

    await _callback.answer("Запустил отправку")

    data = await state.get_data()
    list_users_ids = await crud_service.user.get_all_users()

    for user in list_users_ids:
        try:
            if photo_id := data.get("image_id"):
                await bot.send_photo(
                    chat_id=user.user_tg,
                    photo=photo_id,
                    caption=data["value"],
                )
                continue
            await bot.send_message(
                chat_id=user.user_tg,
                text=data["value"],
            )
        except (TelegramForbiddenError, TelegramBadRequest) as e:
            errors_msg.append(
                f"Не удалось отправить сообщение пользователю {user.user_tg}: {e!s}",
            )
    if errors_msg:
        list_errors = "\n".join(errors_msg)
        message_to_send = f"Ошибки при отправке:\n\n{list_errors}"
        await _callback.message.edit_text(
            message_to_send,
            reply_markup=None,
        )
    else:
        await _callback.message.edit_text(
            "Все сообщения отправлены",
            reply_markup=None,
        )

    await state.clear()


@router.callback_query(
    F.data == "cancel_sending",
    RootPermissionFilter(),
)
async def cancel_send(
    _callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not isinstance(_callback.message, Message):
        return

    await _callback.message.edit_text(
        "Ты решил не отправлять сообщение",
        reply_markup=None,
    )
    await _callback.answer("Операция отменена")
    await state.clear()


@router.message(
    Command("jobs"),
    RootPermissionFilter(),
)
async def get_scheduler_jobs(message: Message) -> None:  # noqa: C901
    jobs = scheduler_instance.list_jobs()

    def user_link(job: dict) -> str:
        tg_id = job.get("user_tg")
        return f'<a href="tg://user?id={tg_id}">{tg_id}</a>' if tg_id else "—"

    entries = []
    for job in jobs:
        next_run = (
            job["next_run_time"].strftime("%Y-%m-%d %H:%M")
            if job.get("next_run_time")
            else "—"
        )
        entry = (
            f"id: <code>{job['id']}</code>\n"
            f"Next run: <code>{next_run}</code>\n"
            f"User: {user_link(job)}"
        )
        entries.append(entry)

    def chunk_entries(
        parts: list[str],
        limit: int = 4000,
        sep: str = "\n\n",
    ) -> list[str]:
        chunks: list[str] = []
        buf: list[str] = []
        cur_len = 0
        for p in parts:
            add_len = (len(sep) if buf else 0) + len(p)
            if cur_len + add_len > limit:
                if buf:
                    chunks.append(sep.join(buf))
                buf = [p]
                cur_len = len(p)
            elif buf:
                buf.append(p)
                cur_len += add_len
            else:
                buf = [p]
                cur_len = len(p)
        if buf:
            chunks.append(sep.join(buf))
        return chunks

    result = "\n\n".join(entries)
    try:
        await message.answer(
            result,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except TelegramBadRequest as e:
        text = str(e).lower()
        if "message is too long" in text or "message_too_long" in text:
            for part in chunk_entries(entries):
                await message.answer(
                    part,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
        else:
            raise
