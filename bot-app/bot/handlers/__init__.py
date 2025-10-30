from aiogram import Router

from bot.handlers.affirmations import router as affirmations_router
from bot.handlers.owner import router as owner_router
from bot.handlers.start_handler import router as start_router
from bot.handlers.user_settings import router as user_settings_router

router = Router()

router.include_router(start_router)
router.include_router(user_settings_router)
router.include_router(owner_router)

router.include_router(affirmations_router)
