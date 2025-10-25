from pydantic import BaseModel


class BaseCommand(BaseModel):
    """Базовая команда"""


class CreateAffirmationCommand(BaseCommand):
    user_tg: int
    affirmation_text: str


class DeleteAffirmationCommand(BaseCommand):
    user_tg: int
    affirmation_id: int
