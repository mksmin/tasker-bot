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
from database import start_engine


async def start_bot() -> Bot:
    bot_token = get_token('TOKEN')

    bot_class = Bot(token=bot_token,
                    default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    return bot_class


async def main() -> None:
    await start_engine()

    bot = await start_bot()

    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    FORMAT = '[%(asctime)s]  %(levelname)s: —— %(message)s'
    logging.basicConfig(level=logging.INFO,
                        datefmt="%Y-%m-%d %H:%M:%S",
                        format=FORMAT)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning('KeyboardInterrupt')
