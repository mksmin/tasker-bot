from datetime import time

from aiogram import Bot
from apscheduler.schedulers.asyncio import (  # type: ignore[import-untyped]
    AsyncIOScheduler,
)
from sqlalchemy import ScalarResult, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from config import logger
from database import UserSettings, connection
from database.crud import crud_manager

from .utils import send_daily_tasks

SCHEDULER = {}


async def setup_scheduler(bot: Bot) -> None:
    scheduler = AsyncIOScheduler()
    SCHEDULER["scheduler"] = scheduler

    @connection
    async def schedule_all(session: AsyncSession) -> None:
        settings: ScalarResult[UserSettings] = await session.scalars(
            select(UserSettings).options(joinedload(UserSettings.user)),
        )
        for setting in settings:
            user_tgid = setting.user.user_tg
            send_time = setting.send_time

            job_id = f"daily_{setting.user_id}"

            logger.info(
                "scheduler get user: %d, with time: %s and id: %s",
                user_tgid,
                send_time.strftime("%H:%M"),
                job_id,
            )

            scheduler.add_job(
                send_daily_tasks,
                trigger="cron",
                hour=send_time.hour,
                minute=send_time.minute,
                args=[user_tgid, bot],
                id=job_id,
                misfire_grace_time=300,
                coalesce=False,
            )

        scheduler.start()

    await schedule_all()


async def update_schedule(
    user_tg_id: int,
    new_time: time,
    bot: Bot,
) -> None:
    scheduler: AsyncIOScheduler = SCHEDULER.get("scheduler")
    user = await crud_manager.user.get_user(user_tg=user_tg_id)
    job_id = f"daily_{user.id}"

    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    scheduler.add_job(
        send_daily_tasks,
        trigger="cron",
        hour=new_time.hour,
        minute=new_time.minute,
        args=[user_tg_id, bot],
        id=job_id,
        misfire_grace_time=300,
        coalesce=False,
    )

    logger.info("Added new job: %s with time %s", job_id, new_time)
