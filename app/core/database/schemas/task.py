from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TaskCreateSchema(BaseModel):
    text_task: str = Field(..., description="Text of the task", max_length=500)
    user_id: int = Field(..., description="User id from the database")

    model_config = ConfigDict(from_attributes=True)


class TaskReadSchema(TaskCreateSchema):
    id: int
    created_at: datetime
    is_done: bool

    model_config = ConfigDict(from_attributes=True)
