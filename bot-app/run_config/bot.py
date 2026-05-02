import logging

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from bot import router as main_router
from bot.middlewares import CreateUserInjectMiddleware
from bot.middlewares import CRUDServiceMiddleware
from bot.middlewares import GetUserMiddleware
from bot.middlewares import GetUserSettingsMiddleware
from config import settings
from database import db_helper

log = logging.getLogger(__name__)

bot_session: AiohttpSession | None = None
if settings.bot.proxy_url and settings.bot.proxy_url.startswith("socks"):
    bot_session = AiohttpSession(
        proxy=settings.bot.proxy_url,
    )

bot = Bot(
    token=settings.bot.token,
    session=bot_session,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)
dp = Dispatcher()

dp.include_router(main_router)


async def on_shutdown() -> None:
    await db_helper.dispose()
    log.info("Disposed database")


dp.shutdown.register(on_shutdown)

dp.message.middleware.register(CRUDServiceMiddleware(db_helper))
dp.message.middleware.register(CreateUserInjectMiddleware())
dp.message.middleware.register(GetUserMiddleware())
dp.message.middleware.register(GetUserSettingsMiddleware())

dp.callback_query.middleware.register(GetUserMiddleware())
dp.callback_query.middleware.register(CRUDServiceMiddleware(db_helper))
dp.callback_query.middleware.register(GetUserSettingsMiddleware())
