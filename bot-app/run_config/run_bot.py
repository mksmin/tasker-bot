import logging
from typing import Any

import uvicorn

from bot.scheduler import setup_scheduler
from config import settings
from config.run import WEBHOOK_MODE
from rabbit_service.broker import broker
from run_config.bot import bot
from run_config.bot import dp

log = logging.getLogger(__name__)


async def start_polling() -> None:
    log.info("Starting bot in polling mode")
    webhook_info = await bot.get_webhook_info()

    if webhook_info.url != "":
        await bot.delete_webhook()
        log.info("Removing bot webhook, because uses polling mode")

    await setup_scheduler(bot)
    await broker.start()
    await dp.start_polling(bot)


async def start_webhooks() -> None:
    config_args: dict[str, Any] = {
        "app": "run_config:app",
        "host": settings.run.host,
        "port": settings.run.port,
        "reload": False,
        "log_config": None,
        "workers": 1,
    }

    config = uvicorn.Config(**config_args)
    server = uvicorn.Server(config)

    log.info("Starting bot in webhook mode")
    await server.serve()


start_app = start_webhooks if settings.run.mode == WEBHOOK_MODE else start_polling
