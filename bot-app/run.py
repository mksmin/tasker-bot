import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot import router as main_router
from bot.middlewares import (
    CreateUserInjectMiddleware,
    CRUDServiceMiddleware,
    GetUserMiddleware,
    GetUserSettingsMiddleware,
)
from bot.scheduler import setup_scheduler
from config import settings
from config.config import logger
from database import db_helper
from rabbit_service.broker import broker


async def start_bot() -> Bot:
    return Bot(
        token=settings.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


async def run_bot() -> None:
    bot = await start_bot()

    dp = Dispatcher()
    dp.include_router(main_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.message.middleware.register(CRUDServiceMiddleware(db_helper))
    dp.message.middleware.register(CreateUserInjectMiddleware())
    dp.message.middleware.register(GetUserMiddleware())
    dp.message.middleware.register(GetUserSettingsMiddleware())
    dp.callback_query.middleware.register(GetUserSettingsMiddleware())
    await bot.delete_webhook(
        drop_pending_updates=True,
    )
    await setup_scheduler(bot)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


async def main() -> None:
    await asyncio.gather(
        broker.start(),
        run_bot(),
    )


async def on_startup() -> None:
    pass


async def on_shutdown() -> None:
    await db_helper.dispose()
    logger.info("Disposed database")


if __name__ == "__main__":
    FORMAT = "[%(asctime)s]  %(levelname)s: —— %(message)s"
    logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S", format=FORMAT)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt")
