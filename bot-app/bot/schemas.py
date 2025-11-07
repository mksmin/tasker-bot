from datetime import datetime
from typing import TypedDict


class JobInfo(TypedDict, total=False):
    id: str
    name: str | None
    next_run_time: datetime | None
    trigger: str
    hour: str | None
    minute: str | None
    timezone: str | None
    coalesce: bool
    misfire_grace_time: int | None
    user_id: int | None
    user_tg: int | None
