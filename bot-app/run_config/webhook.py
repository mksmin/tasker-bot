import logging

from aiogram.types import Update
from fastapi import FastAPI
from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse

from config import settings
from run_config.bot import bot
from run_config.bot import dp
from run_config.fastapi_lifespan import lifespan

log = logging.getLogger(__name__)


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


@app.get(
    settings.run.webhook.path + "/health",
)
async def health() -> JSONResponse:
    return JSONResponse(
        content={"status": "ok"},
        status_code=status.HTTP_200_OK,
    )
