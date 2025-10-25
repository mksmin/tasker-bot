from faststream.rabbit import RabbitBroker

from config import settings
from rabbit_service.affirmations import router as affirmations_router

broker = RabbitBroker(settings.rabbit.url)

broker.include_router(
    affirmations_router,
)
