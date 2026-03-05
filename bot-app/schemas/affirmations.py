from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class AffirmationBaseSchema(BaseModel):
    text: str = Field(..., alias="text_task")

    model_config = ConfigDict(from_attributes=True)


class AffirmationReadSchema(AffirmationBaseSchema):
    id: int
    created_at: datetime
