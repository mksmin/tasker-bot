from datetime import datetime
from typing import TypedDict

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from apscheduler.schedulers.asyncio import (  # type: ignore[import-untyped]
    AsyncIOScheduler,
)
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import ScalarResult, select
from sqlalchemy.orm import joinedload

from config import logger
from database import UserSettings, db_helper
from schemas.users import (
    UserSettingsWithUserReadSchema,
)


class JobInfo(TypedDict, total=False):
    id: str
    name: str | None
    next_run_time: datetime | None
    trigger: str
    hour: str | None
    minute: str | None
    timezone: str | None
    coalesce: bool
    misfire_grace_time: int | None
    user_id: int | None
    user_tg: int | None


class DailyTaskScheduler:
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
                user_with_settings = UserSettingsWithUserReadSchema.model_validate(
                    setting,
                )
                if not user_with_settings.send_enable:
                    continue

                self.add_or_update_job(user_with_settings)

            self.scheduler.start()

    async def safe_send_wrapper(
        self,
        user_id: int,
        user_tg: int,
    ) -> None:
        from bot.dependencies import send_daily_tasks  # noqa: PLC0415

        assert self._bot is not None, "Bot instance must be set before scheduling jobs"

        try:
            await send_daily_tasks(self._bot, user_tg)
        except TelegramForbiddenError as e:
            logger.warning(
                "Removing job for user %d due to TelegramForbiddenError: %s",
                user_id,
                e,
            )
            self.remove_job(user_id)

    def add_or_update_job(
        self,
        user_settings: UserSettingsWithUserReadSchema,
    ) -> None:
        job_id = f"daily_{user_settings.user.id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        self.scheduler.add_job(
            self.safe_send_wrapper,
            trigger="cron",
            hour=user_settings.send_time.hour,
            minute=user_settings.send_time.minute,
            args=[
                user_settings.user.id,
                user_settings.user.user_tg,
            ],
            id=job_id,
            misfire_grace_time=300,
            coalesce=False,
        )
        logger.info(
            "Scheduled job %s at time %s for user %s",
            job_id,
            user_settings.send_time,
            user_settings.user.id,
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

    def list_jobs(self) -> list[JobInfo]:
        items: list[JobInfo] = []
        for job in self.scheduler.get_jobs():
            tz = None
            hour = None
            minute = None
            if isinstance(job.trigger, CronTrigger):
                tz = str(job.trigger.timezone)
                minute = str(job.trigger.fields[1])
                hour = str(job.trigger.fields[2])

            args = list(job.args or [])
            user_id = None
            user_tg = None
            len_args_constant = 2
            if (
                len(args) >= len_args_constant
                and isinstance(args[0], int)
                and isinstance(args[1], int)
            ):
                user_id, user_tg = args[0], args[1]

            items.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time,
                    "trigger": str(job.trigger),
                    "hour": hour,
                    "minute": minute,
                    "timezone": tz,
                    "coalesce": job.coalesce,
                    "misfire_grace_time": job.misfire_grace_time,
                    "user_id": user_id,
                    "user_tg": user_tg,
                },
            )
        return items


scheduler_instance = DailyTaskScheduler()


async def setup_scheduler(
    bot: Bot,
) -> None:
    scheduler_instance.set_bot(bot)
    await scheduler_instance.init_jobs_from_db()
