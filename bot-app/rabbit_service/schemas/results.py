from pydantic import BaseModel

from schemas.affirmations import AffirmationReadSchema


class BaseResult(BaseModel):
    status: str
    message: str | None = None


class AffirmationResult(BaseResult):
    affirmation: AffirmationReadSchema | None = None


class AffirmationsListResult(BaseResult):
    affirmations: list[AffirmationReadSchema] = []
