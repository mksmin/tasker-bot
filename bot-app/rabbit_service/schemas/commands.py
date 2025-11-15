from pydantic import BaseModel


class BaseCommand(BaseModel):
    """Базовая команда"""


class CreateAffirmationCommand(BaseCommand):
    user_tg: int
    affirmation_text: str


class DeleteAffirmationCommand(BaseCommand):
    user_tg: int
    affirmation_id: int


class UpdateAffirmationCommand(BaseCommand):
    user_tg: int
    affirmation_id: int
    affirmation_in: str


class AffirmationsSettings(BaseCommand):
    count_tasks: int | None = None
    send_time: str | None = None
    send_enable: bool | None = None


class PatchAffirmationsSettingsCommand(BaseCommand):
    user_tg: int
    settings_in: AffirmationsSettings | None = None
