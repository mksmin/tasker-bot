import os

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.handlers import send_daily_tasks
from database import connection, User, UserSettings
from database import requests as rq
from config import logger


# async def setup_scheduler(bot: Bot):
#     scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
#
#     @connection
#     async def daily_send(session):
#         users = await session.scalars(
#             select(User.user_tg)
#         )
#
#         logger.info(f'scheduled get user: {users}')
#
#         for user in users:
#             try:
#                 await send_daily_tasks(
#                     user_tgid=user,
#                     bot=bot
#                 )
#             except Exception as e:
#                 logger.error(f'Error during sending tasks: {e}')
#                 continue
#
#     scheduler.add_job(
#         daily_send,
#         'cron',
#         hour=9,
#         minute=0,
#         timezone='Europe/Moscow',
#         misfire_grace_time=300,
#         coalesce=False
#     )
#
#     scheduler.start()


async def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()

    @connection
    async def schedule_all(session):
        settings: list[UserSettings] = await session.scalars(
            select(UserSettings).options(joinedload(UserSettings.user))
        )
        for setting in settings:

            user_tgid = setting.user.user_tg
            send_time = setting.send_time

            job_id = f"daily_{setting.user_id}"

            logger.info(f'scheduled get user: {user_tgid}, with time: {send_time} and id: {job_id}')

            scheduler.add_job(
                send_daily_tasks,
                trigger='cron',
                hour=send_time.hour,
                minute=send_time.minute,
                args=[user_tgid, bot],
                id=job_id,
                misfire_grace_time=300,
                coalesce=False
            )

        scheduler.start()

    await schedule_all()

