from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.handler_filtres import HasUserFilter

router = Router()


@router.message(
    CommandStart(),
    HasUserFilter(),
    flags={
        "create_user": True,
    },
)
async def cmd_start(
    message: Message,
) -> None:
    await message.answer(
        "Привет! \n\n"
        "Отправь мне любые афоризмы или аффирмации <i>(по одной шт за раз)</i>, "
        "а я буду каждый день присылать тебе 5 случайных! \n\n"
        "Обычно я отправляю в 9 утра по Москве. Используй команду /settings, "
        "чтобы изменить время отправки",
    )
