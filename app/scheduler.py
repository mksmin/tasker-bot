import os

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.handlers import send_daily_tasks
from config import logger
from database import connection, User


async def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()

    @connection
    async def daily_send(session):
        users = await session.scalars(
            select(User.user_tg)
        )

        logger.info(f'scheduled get user: {users}')

        for user in users:
            await send_daily_tasks(
                user_tgid=user,
                bot=bot
            )

    scheduler.add_job(
        daily_send,
        'cron',
        hour=23,
        minute=31,
        timezone='Europe/Moscow',
        misfire_grace_time=300,
        coalesce=False
    )

    scheduler.start()
