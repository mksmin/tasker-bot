from pydantic import BaseModel

from database.schemas import TaskReadSchema


class BaseResult(BaseModel):
    status: str
    message: str | None = None


class AffirmationResult(BaseResult):
    affirmation: TaskReadSchema | None = None


class AffirmationsListResult(BaseResult):
    affirmations: list[TaskReadSchema] = []
