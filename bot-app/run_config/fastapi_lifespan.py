import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from aiogram.exceptions import TelegramNetworkError
from fastapi import FastAPI

from bot.scheduler import setup_scheduler
from config import settings
from rabbit_service.broker import broker
from run_config.bot import bot
from run_config.bot import dp

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(
    app: FastAPI,  # noqa: ARG001
) -> AsyncGenerator[None, None]:
    webhook_info = await bot.get_webhook_info()
    log.info(
        "Webhook url: %s, ip: %s",
        webhook_info.url,
        webhook_info.ip_address,
    )
    if webhook_info.url != settings.run.webhook.url:
        log.info("Updating webhook to: %s", settings.run.webhook.url)
        await bot.set_webhook(
            url=settings.run.webhook.url,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True,
        )
        webhook_info = await bot.get_webhook_info()
        log.info(
            "Updated webhook url: %s, ip: %s",
            webhook_info.url,
            webhook_info.ip_address,
        )
    else:
        log.info("Webhook is up to date.")

    try:
        me = await bot.get_me()
        log.info("Бот успешно запущен как @%s", me.username)
    except TelegramNetworkError:
        log.exception("Ошибка подключения")
        raise
    await setup_scheduler(bot)
    await broker.start()
    yield
