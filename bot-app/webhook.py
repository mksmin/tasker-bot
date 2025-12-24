import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from fastapi import (
    FastAPI,
    Request,
    status,
)
from fastapi.responses import JSONResponse

from bot import router as main_router
from bot.middlewares import (
    CreateUserInjectMiddleware,
    CRUDServiceMiddleware,
    GetUserMiddleware,
    GetUserSettingsMiddleware,
)
from bot.scheduler import setup_scheduler
from config import logger, settings
from database import db_helper

log = logging.getLogger(__name__)

bot = Bot(
    token=settings.bot.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()

dp.include_router(main_router)


async def on_shutdown() -> None:
    await db_helper.dispose()
    logger.info("Disposed database")


dp.shutdown.register(on_shutdown)

dp.message.middleware.register(CRUDServiceMiddleware(db_helper))
dp.message.middleware.register(CreateUserInjectMiddleware())
dp.message.middleware.register(GetUserMiddleware())
dp.message.middleware.register(GetUserSettingsMiddleware())

dp.callback_query.middleware.register(GetUserMiddleware())
dp.callback_query.middleware.register(CRUDServiceMiddleware(db_helper))
dp.callback_query.middleware.register(GetUserSettingsMiddleware())


@asynccontextmanager
async def lifespan(
    app: FastAPI,  # noqa: ARG001
) -> AsyncGenerator[None, None]:
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != settings.run.webhook.url:
        log.info("Updating webhook to: %s", settings.run.webhook.url)
        await bot.set_webhook(
            url=settings.run.webhook.url,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True,
        )
    else:
        log.info("Webhook is up to date.")

    await setup_scheduler(bot)
    yield
    log.info("Deleting webhook")
    await bot.delete_webhook()


app = FastAPI(
    lifespan=lifespan,
)


@app.post(
    settings.run.webhook.path,
)
async def handle_update(
    request: Request,
) -> JSONResponse:
    try:
        data = await request.json()
        update = Update.model_validate(
            data,
            context={"bot": bot},
        )
        await dp.feed_update(
            bot,
            update,
        )
    except Exception:
        log.exception("Error in webhook")

    return JSONResponse(
        content={"status": "ok"},
        status_code=status.HTTP_200_OK,
    )
