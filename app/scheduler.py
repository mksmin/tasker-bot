import os

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from database import connection, User
from app.handlers import send_daily_tasks

async def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()

    @connection
    async def daily_send(session):
        users = session.scalars(
            select(User.user_tg)
        )

        for user in users:
            await send_daily_tasks(user, bot)

        scheduler.add_job(
            daily_send,
            'cron',
            hour=22,
            minute=10,
            timezone='Europe/Moscow',
        )

        scheduler.start()

