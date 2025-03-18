# import lib
import asyncio
import logging

# import from lib
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from pathlib import Path

# import from modules
from app.handlers import router
from config.config import logger, get_token
from app.scheduler import setup_scheduler
from database import db_helper, start_engine
from config import settings


async def start_bot() -> Bot:
    bot_class = Bot(token=settings.bot.token,
                    default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    return bot_class


async def main() -> None:
    # await start_engine()

    bot = await start_bot()

    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await bot.delete_webhook(drop_pending_updates=True)
    await setup_scheduler(bot)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


async def on_startup() -> None:
    pass


async def on_shutdown() -> None:
    await db_helper.dispose()
    logger.info(f'Disposed database')


if __name__ == '__main__':
    FORMAT = '[%(asctime)s]  %(levelname)s: —— %(message)s'
    logging.basicConfig(level=logging.INFO,
                        datefmt="%Y-%m-%d %H:%M:%S",
                        format=FORMAT)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning('KeyboardInterrupt')
