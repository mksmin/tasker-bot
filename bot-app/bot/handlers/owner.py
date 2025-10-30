from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import keyboards as kb
from bot import statesuser as st
from bot.handler_filtres.user_filter import RootPermissionFilter

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
) -> None:
    if not isinstance(_callback.message, Message):
        return
    if not isinstance(_callback.bot, Bot):
        return

    bot = _callback.bot
    errors_msg = []

    await _callback.answer("Запустил отправку")

    data = await state.get_data()
    list_users_ids = [...]  # TODO: добавить метод выгрузки всех id пользователей бота

    for user_id in list_users_ids:
        try:
            if photo_id := data.get("image_id"):
                await bot.send_photo(
                    chat_id=user_id,
                    photo=photo_id,
                    caption=data["value"],
                )
                continue
            await bot.send_message(
                chat_id=user_id,
                text=data["value"],
            )
        except (TelegramForbiddenError, TelegramBadRequest) as e:
            errors_msg.append(
                f"Не удалось отправить сообщение пользователю {user_id}: {e!s}",
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
