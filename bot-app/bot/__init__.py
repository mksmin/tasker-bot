__all__ = (
    "router",
    "send_daily_tasks",
)

from aiogram import Router

from bot.dependencies import send_daily_tasks
from bot.handlers import router as handlers_router

router = Router()

router.include_router(handlers_router)
