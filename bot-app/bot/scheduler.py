from datetime import time

from aiogram import Bot
from apscheduler.schedulers.asyncio import (  # type: ignore[import-untyped]
    AsyncIOScheduler,
)
from sqlalchemy import ScalarResult, select
from sqlalchemy.orm import joinedload

from config import logger
from database import UserSettings, db_helper

from .utils import send_daily_tasks


class DailyTaskSheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self._bot: Bot | None = None

    def set_bot(
        self,
        bot: Bot,
    ) -> None:
        self._bot = bot

    async def init_jobs_from_db(
        self,
    ) -> None:
        async for session in db_helper.session_getter():
            settings: ScalarResult[UserSettings] = await session.scalars(
                select(UserSettings).options(
                    joinedload(UserSettings.user),
                ),
            )
            for setting in settings:
                self.add_or_update_job(
                    user_id=setting.user_id,
                    user_tg_id=setting.user.user_tg,
                    send_time=setting.send_time,
                )

            self.scheduler.start()

    def add_or_update_job(
        self,
        user_id: int,
        user_tg_id: int,
        send_time: time,
    ) -> None:
        job_id = f"daily_{user_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        self.scheduler.add_job(
            send_daily_tasks,
            trigger="cron",
            hour=send_time.hour,
            minute=send_time.minute,
            args=[user_tg_id, self._bot],
            id=job_id,
            misfire_grace_time=300,
            coalesce=False,
        )
        logger.info(
            "Scheduled job %s at time %s for user %s",
            job_id,
            send_time,
            user_id,
        )

    def remove_job(
        self,
        user_id: int,
    ) -> None:
        job_id = f"daily_{user_id}"
        job = self.scheduler.get_job(job_id)
        if job:
            self.scheduler.remove_job(job_id)
            logger.info(
                "Removed job %s for user %s",
                job_id,
                user_id,
            )


scheduler_instance = DailyTaskSheduler()


async def setup_scheduler(bot: Bot) -> None:
    scheduler_instance.set_bot(bot)
    await scheduler_instance.init_jobs_from_db()
