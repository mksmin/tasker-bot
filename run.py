# import lib
import asyncio
import logging

# import from lib
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# import from modules
from app.bot.middlewares.user_init import UserMiddleware
from app.handlers import router
from app.rabbit_tasks import broker
from app.scheduler import setup_scheduler
from config import settings, logger
from database import db_helper, DbSessionMiddleware


async def start_bot() -> Bot:
    bot_class = Bot(token=settings.bot.token,
                    default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    return bot_class


async def run_bot():
    bot = await start_bot()

    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.message.middleware.register(DbSessionMiddleware())
    dp.message.middleware.register(UserMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
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
    logger.info(f'Disposed database')
    await broker.stop()
    logger.info(f'Stopped broker')


if __name__ == '__main__':
    FORMAT = '[%(asctime)s]  %(levelname)s: —— %(message)s'
    logging.basicConfig(level=logging.INFO,
                        datefmt="%Y-%m-%d %H:%M:%S",
                        format=FORMAT)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning('KeyboardInterrupt')
