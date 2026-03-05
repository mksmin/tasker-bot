from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class SortBy(str, Enum):
    CREATED_AT = "created_at"
    TEXT = "text"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class AffirmationBaseSchema(BaseModel):
    text: str = Field(..., alias="text_task")

    model_config = ConfigDict(from_attributes=True)


class AffirmationReadSchema(AffirmationBaseSchema):
    id: int
    created_at: datetime
