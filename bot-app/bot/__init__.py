__all__ = (
    "router",
    "send_daily_tasks",
)

from aiogram import Router

from bot.handlers.affirmations import router as affirmations_router
from bot.handlers.start_handler import router as start_router
from bot.handlers.user_settings import router as user_settings_router
from bot.utils import send_daily_tasks

router = Router()

router.include_router(start_router)
router.include_router(user_settings_router)
router.include_router(affirmations_router)
